"""
Data Visualization Module

This module provides functions for visualizing job market data.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Optional, Tuple, List, Union, Dict

class JobMarketVisualizer:
    """Class for creating visualizations of job market data."""
    
    def __init__(self, style: str = "white", context: str = "paper", palette: str = "flare"):
        """
        Initialize the job market visualizer.
        
        Args:
            style: Seaborn style (whitegrid, darkgrid, white, dark, ticks)
            context: Seaborn context (paper, notebook, talk, poster)
            palette: Default color palette
        """
        self.palette = palette
        sns.set_theme(style=style, context=context)
        plt.rcParams['figure.figsize'] = (12, 6)
    
    def plot_jobs_by_location(self, df: pd.DataFrame, 
                             title: str = "Jobs By Locations",
                             save_path: Optional[str] = None) -> None:
        """
        Create a bar plot showing job counts by location.
        
        Args:
            df: DataFrame with job data
            title: Plot title
            save_path: Path to save the figure (optional)
        """
        # Group and sort data
        location_df = df['Location'].value_counts().sort_values(ascending=False)
        
        # Create figure
        plt.figure(figsize=(10, max(6, len(location_df) * 0.4)))
        
        # Create barplot with Seaborn
        palette = sns.color_palette(self.palette, len(location_df))[::-1]  # Reverse colors
        ax = sns.barplot(y=location_df.index, x=location_df.values, palette=palette)
        
        # Add data labels
        for index, value in enumerate(location_df.values):
            ax.text(value + 1, index, str(value), va='center')
        
        # Set labels and title
        ax.set(xlabel='Number of Jobs', ylabel='Locations', title=title)
        
        # Save if path is provided
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
        plt.show()
    
    def plot_salary_by_experience(self, df: pd.DataFrame,
                                 title: str = "Average Salary by Experience",
                                 save_path: Optional[str] = None) -> None:
        """
        Create a line plot showing salary trends by experience.
        
        Args:
            df: DataFrame with job data
            title: Plot title
            save_path: Path to save the figure (optional)
        """
        # Compute mean salaries by experience
        mean_salaries = df.groupby('exp_max', as_index=False).agg({
            'Min_Salary': 'mean', 
            'Max_Salary': 'mean'
        })
        
        # Convert salary values to millions
        mean_salaries['Min_Salary'] /= 1e6
        mean_salaries['Max_Salary'] /= 1e6
        
        # Create the line chart
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=mean_salaries, x='exp_max', y='Min_Salary', label='Average Min Salary')
        sns.lineplot(data=mean_salaries, x='exp_max', y='Max_Salary', label='Average Max Salary')
        
        # Labels and title
        plt.xlabel("Experience (Years)")
        plt.ylabel("Salary (Million VND)")
        plt.title(title)
        plt.legend()
        
        
        # Save if path is provided
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
        plt.show()
    
    def plot_jobs_by_date(self, df: pd.DataFrame,
                         title: str = "Jobs By Date",
                         save_path: Optional[str] = None) -> None:
        """
        Create a line plot showing job counts by date.
        
        Args:
            df: DataFrame with job data
            title: Plot title
            save_path: Path to save the figure (optional)
        """
        # Convert Date column to datetime format (if not already)
        df = df.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Extract day and month, then keep the original Date for sorting
        df['DayMonth'] = df['Date'].dt.strftime('%d-%b')  # Format: "15-Mar"
        
        # Count job occurrences per day
        job_df = df.groupby(['Date', 'DayMonth']).size().reset_index(name='JobCount')
        
        # Sort by actual Date to maintain chronological order
        job_df = job_df.sort_values(by='Date')
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        ax = sns.lineplot(x=job_df['DayMonth'], y=job_df['JobCount'])
        
        # Rotate x-axis labels for better readability
        ax.set_xticklabels(ax.get_xticklabels(), rotation=270, ha="left")
        
        # Set labels and title
        ax.set(xlabel='Date', ylabel='Number of Jobs', title=title)
        
        # Save if path is provided
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
        plt.show()
    
    def plot_salary_heatmap(self, df: pd.DataFrame,
                           title: str = "Salary by Location and Experience",
                           save_path: Optional[str] = None) -> None:
        """
        Create a heatmap showing salary by location and experience.
        
        Args:
            df: DataFrame with job data
            title: Plot title
            save_path: Path to save the figure (optional)
        """
        # Ensure columns are numeric
        df = df.copy()
        df['Min_Salary'] = pd.to_numeric(df['Min_Salary'], errors='coerce')
        df['exp_min'] = pd.to_numeric(df['exp_min'], errors='coerce')
        
        # Group by Location and exp_min, then get the minimum salary
        heatmap_data = df.groupby(['Location', 'exp_min'])['Min_Salary'].mean().reset_index()
        
        # Convert to millions for better readability
        heatmap_data['Min_Salary'] /= 1e6
        
        # Pivot the data to create a matrix
        heatmap_pivot = heatmap_data.pivot(
            index='exp_min', 
            columns='Location', 
            values='Min_Salary'
        ).fillna(0)
        
        # Create the heatmap
        plt.figure(figsize=(14, 8))
        ax = sns.heatmap(heatmap_pivot, cmap='flare', annot=True, fmt=",.1f", linewidths=0.5)
        
        # Set labels and title
        ax.set_xlabel("Location")
        ax.set_ylabel("Minimum Experience (Years)")
        ax.set_title(title)
        
        # Save if path is provided
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
        plt.show()
    
    def plot_experience_by_job_level(self, df: pd.DataFrame,
                                   title: str = "Experience Requirements by Job Level",
                                   save_path: Optional[str] = None) -> None:
        """
        Create a boxplot showing experience requirements by job level.
        
        Args:
            df: DataFrame with job data
            title: Plot title
            save_path: Path to save the figure (optional)
        """
        # Melt the dataset to reshape 'exp_min' and 'exp_max' into a single column
        experience_melted = df.melt(
            id_vars=['Job Level'], 
            value_vars=['exp_min', 'exp_max'],
            var_name='Experience Type', 
            value_name='Experience (Years)'
        )
        
        # Create a boxplot
        plt.figure(figsize=(12, 8))
        sns.boxplot(
            data=experience_melted, 
            x='Job Level', 
            y='Experience (Years)', 
            hue='Experience Type', 
            palette=['#431c76', '#e13661']
        )
        
        plt.title(title)
        plt.xlabel('Job Level')
        plt.ylabel('Years of Experience')
        plt.legend(title='Experience Type')
        
        # Save if path is provided
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
        plt.show()
    
    def plot_top_job_titles(self, df: pd.DataFrame, n: int = 10,
                          title: str = "Top Job Titles",
                          save_path: Optional[str] = None) -> None:
        """
        Create a bar plot showing the most common job titles.
        
        Args:
            df: DataFrame with job data
            n: Number of top job titles to show
            title: Plot title
            save_path: Path to save the figure (optional)
        """
        # Get top N most frequent job titles
        top_jobs = df['Job Title'].value_counts().nlargest(n)
        
        # Create bar plot
        plt.figure(figsize=(12, 8))
        palette = sns.color_palette(self.palette, len(top_jobs))[::-1]
        sns.barplot(x=top_jobs.values, y=top_jobs.index, palette=palette)
        
        plt.xlabel("Number of Job Postings")
        plt.ylabel("Job Title")
        plt.title(title)
        
        # Add data labels
        for i, v in enumerate(top_jobs.values):
            plt.text(v + 0.5, i, str(v), va='center')
        
        # Save if path is provided
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
        plt.show()
    
    def plot_top_companies(self, df: pd.DataFrame, n: int = 10,
                         title: str = "Top Companies Hiring",
                         save_path: Optional[str] = None) -> None:
        """
        Create a bar plot showing the companies with the most job postings.
        
        Args:
            df: DataFrame with job data
            n: Number of top companies to show
            title: Plot title
            save_path: Path to save the figure (optional)
        """
        # Get top N companies with most job postings
        top_companies = df['Company'].value_counts().nlargest(n)
        
        # Create bar plot
        plt.figure(figsize=(12, 8))
        sns.barplot(x=top_companies.values, y=top_companies.index, palette='Blues_r')
        
        plt.xlabel("Number of Job Postings")
        plt.ylabel("Company")
        plt.title(title)
        
        # Add data labels
        for i, v in enumerate(top_companies.values):
            plt.text(v + 0.5, i, str(v), va='center')
        
        # Save if path is provided
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
        plt.show()
    
    def plot_skills(self, skill_df: pd.DataFrame, title: str,
                  color: str = "Blues_r", top_n: Optional[int] = None,
                  save_path: Optional[str] = None) -> None:
        """
        Create a bar plot showing skill frequencies.
        
        Args:
            skill_df: DataFrame with skill counts
            title: Plot title
            color: Color palette
            top_n: Number of top skills to show (optional)
            save_path: Path to save the figure (optional)
        """
        if skill_df.empty:
            print(f"No data to plot for '{title}'")
            return
        
        # Filter to top N skills if specified
        if top_n is not None:
            skill_df = skill_df.head(top_n)
        
        # Adjust figure height dynamically based on number of skills
        plt.figure(figsize=(12, max(6, len(skill_df) * 0.4)))
        
        # Create bar plot
        ax = sns.barplot(x="Count", y="Skill", data=skill_df, palette=color)
        
        # Add data labels
        for i, v in enumerate(skill_df["Count"]):
            ax.text(v + 0.5, i, str(v), va='center')
        
        # Set labels and title
        plt.xlabel("Frequency")
        plt.ylabel("Skills")
        plt.title(title)
        
        # Save if path is provided
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
        plt.show()