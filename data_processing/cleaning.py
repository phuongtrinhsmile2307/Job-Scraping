"""
Data Cleaning Module

This module handles cleaning and preprocessing the job data scraped from CareerViet.
"""
import re
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta

class JobDataCleaner:
    """Class for cleaning and preprocessing job data."""
    
    def __init__(self, exchange_rate=25505):
        """
        Initialize the job data cleaner.
        
        Args:
            exchange_rate: USD to VND exchange rate
        """
        self.exchange_rate = exchange_rate
        self.today = date.today()
    
    def clean(self, df):
        """
        Clean and preprocess the job data.
        
        Args:
            df: Pandas DataFrame with job data
            
        Returns:
            Cleaned DataFrame
        """
        # Make a copy to avoid modifying the original
        cleaned_df = df.copy()
        
        # Clean and transform each column
        cleaned_df = self._clean_dates(cleaned_df)
        cleaned_df = self._clean_location(cleaned_df)
        cleaned_df = self._clean_text_fields(cleaned_df)
        cleaned_df = self._clean_salary(cleaned_df)
        cleaned_df = self._clean_experience(cleaned_df)
        
        # Drop duplicates
        cleaned_df = cleaned_df.drop_duplicates()
        
        return cleaned_df
    
    def _clean_dates(self, df):
        """Clean date fields."""
        # Handle 'Date' column
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        
        # Fill NaN values in 'Expire Date' with 'unknown'
        df['Expire Date'].fillna('unknown', inplace=True)
        
        # Convert "Expire Date" column
        df["Expire Date"] = df["Expire Date"].apply(self._convert_expire_date)
        
        return df
    
    def _convert_expire_date(self, x):
        """Convert expire date string to date object."""
        if isinstance(x, str):
            if "Hôm nay" in x:
                return self.today
            elif "ngày" in x:  # Example: "4 ngày"
                try:
                    days = int(re.search(r'(\d+)', x).group(1))
                    return self.today + timedelta(days=days)
                except (AttributeError, ValueError):
                    return 'unknown'
            elif "-" in x:  # Example: "31-03-2025"
                try:
                    return datetime.strptime(x, "%d-%m-%Y").date()
                except ValueError:
                    return 'unknown'  # Handle incorrect formats safely
        return 'unknown'  # Default for other cases
    
    def _clean_location(self, df):
        """Clean location field."""
        # Remove unnecessary characters and standardize format
        df['Location'] = df['Location'].str.replace('\r\n', ',', regex=True)
        return df
    
    def _clean_text_fields(self, df):
        """Clean and standardize text fields."""
        # Uppercase first letter
        for col in ['Job Title', 'Company']:
            df[col] = df[col].str.title()
        
        # Clean salary text
        df['Salary'] = df['Salary'].str.title()
        
        return df
    
    def _clean_salary(self, df):
        """Clean and normalize salary information."""
        # Extract Min Salary, Max Salary, and Currency using regex
        df[['Min_Salary', 'Max_Salary', 'Currency']] = df['Salary'].str.extract(
            r'([\d,]+)?[^\d]+([\d,]+)?\s*([A-Za-z]+)?'
        )
        
        # Convert salary columns to numeric
        for col in ['Min_Salary', 'Max_Salary']:
            df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')
        
        # Convert "Tr VND" salaries to VND (multiply by 1,000,000)
        tr_mask = df['Currency'] == 'Tr'
        df.loc[tr_mask, ['Min_Salary', 'Max_Salary']] = df.loc[tr_mask, ['Min_Salary', 'Max_Salary']] * 1000000
        
        # Convert "USD" salaries to VND using exchange rate
        usd_mask = df['Salary'].str.contains('Usd', na=False)
        df.loc[usd_mask, ['Min_Salary', 'Max_Salary']] = df.loc[usd_mask, ['Min_Salary', 'Max_Salary']] * self.exchange_rate
        
        # Handle "Lên Đến X Tr Vnd" (set Min = mean, Max = X * 1,000,000)
        up_to_mask = df['Salary'].str.contains('Lên Đến', na=False)
        mean_min = df['Min_Salary'].mean()
        df.loc[up_to_mask, 'Min_Salary'] = mean_min
        
        # Extract value and convert to VND for "Lên Đến X Tr Vnd"
        up_to_values = df.loc[up_to_mask, 'Salary'].str.extract(r'Lên Đến (\d+)')[0]
        df.loc[up_to_mask, 'Max_Salary'] = pd.to_numeric(up_to_values, errors='coerce') * 1000000
        
        # Remove the Currency column
        df = df.drop(columns=['Currency'])
        
        # Replace NaN salaries with the mean
        mean_min_salary = df['Min_Salary'].mean()
        df['Min_Salary'].fillna(round(mean_min_salary, 0), inplace=True)
        
        mean_max_salary = df['Max_Salary'].mean() 
        df['Max_Salary'].fillna(round(mean_max_salary, 0), inplace=True)
        
        return df
    
    def _clean_experience(self, df):
        """Clean and normalize experience information."""
        # Ensure Experience is a string and remove spaces
        df['Experience'] = df['Experience'].astype(str).str.title().str.strip()
        
        # Extract min and max years
        df[['exp_min', 'exp_max']] = df['Experience'].str.split('-', expand=True)
        
        # Extract numeric values and convert to float
        df['exp_min'] = pd.to_numeric(
            df['exp_min'].str.extract(r'(\d+\.?\d*)')[0].str.strip(), 
            errors='coerce'
        )
        
        df['exp_max'] = pd.to_numeric(
            df['exp_max'].str.extract(r'(\d+\.?\d*)')[0].str.strip(), 
            errors='coerce'
        )
        
        # Handle "Chưa Có Kinh Nghiệm" (No Experience)
        no_exp_mask = df['Experience'].str.contains('Chưa Có Kinh Nghiệm', na=False)
        df.loc[no_exp_mask, ['exp_min', 'exp_max']] = 0
        
        # Handle "Trên X năm" (More than X years)
        over_mask = df['Experience'].str.contains('Trên', na=False)
        df.loc[over_mask, 'exp_max'] = np.nan
        
        # Handle "Lên Đến X năm" (Up to X years)
        up_to_mask = df['Experience'].str.contains('Lên Đến', na=False)
        df.loc[up_to_mask, 'exp_min'] = 0
        
        # Fill NaN with mean values
        mean_exp_min = df['exp_min'].mean()
        df['exp_min'].fillna(round(mean_exp_min, 0), inplace=True)
        
        mean_exp_max = df['exp_max'].mean()
        df['exp_max'].fillna(round(mean_exp_max, 0), inplace=True)
        
        # Final cleanup: ensure all values are proper float
        df['exp_min'] = df['exp_min'].astype(float)
        df['exp_max'] = df['exp_max'].astype(float)
        
        return df
    
    def filter_data_jobs(self, df):
        """
        Filter DataFrame to include only data-related jobs.
        
        Args:
            df: Pandas DataFrame with job data
            
        Returns:
            Filtered DataFrame with only data-related jobs
        """
        # Keywords to filter data jobs
        keywords = [
            'Data', 'Analyst', 'Phân Tích', 'Dữ Liệu', 'Intelligence', 
            'Machine Learning', 'Scientist', 'Công Nghệ', 'Ai', 'Statistics', 'Research',
            'Researcher', 'Ecommerce', 'Digital', 'Nghiên Cứu', 'Crm', 'Erp', 'Sap',
            'System', 'Database', 'Bi', 'Sql', 'Python', 'Etl', 'Insights', 'Analytics',
            'Artificial Intelligence', 'Clustering', 'Regression', 'Dashboard', 'Excel', 
            'Power Bi', 'Visualization', 'Reporting', 'Forecasting', 'Quantitative',
            'Modelling', 'Dự Báo', 'Báo Cáo', 'Mining', 'Analysis', 'Analytic', 'Labeling',
            'Platform', 'Số Liệu', 'Automation', 'Cntt', 'Software Engineer'
        ]
        
        # Create a regex pattern with word boundaries (\b)
        pattern = r'\b(?:' + '|'.join(map(re.escape, keywords)) + r')\b'
        
        # Filter rows that contain at least one whole-word keyword in 'Job Title'
        return df[df['Job Title'].str.contains(pattern, case=False, na=False, regex=True)]
    
    def filter_analyst_jobs(self, df):
        # Keywords to filter analyst jobs
        keywords=['Analyst','Phân Tích']

        # Create a regex pattern with word boundaries (\b)
        pattern = r'\b(?:' + '|'.join(map(re.escape, keywords)) + r')\b'

        # Filter rows that contain at least one whole-word keyword in 'Job Title'
        return df[df['Job Title'].str.contains(pattern, case=False, na=False, regex=True)]
    
