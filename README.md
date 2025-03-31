## Overview
This project scrapes job data from CareerViet, a Vietnamese job listing site, focusing on data-related positions. 
The goal is to analyze the labor market and gain insights by answering these questions:
1. Which locations have the highest concentration of data-related job postings?
2. How do salary distributions vary by experience level and location?
3. What are the most in-demand technical and soft skills for analyst roles?
4. When were the most job postings recorded?"
            
## Tools & Technologies
**Python**:
- `Selenium`: automated web scraping.
- `BeautifulSoup`: HTML parsing.
- `Pandas`: data manipulation and transformation.
- `Matplotlib`, `Seaborn` & `Plotly`: data visualization.
- `Streamlit`: building and deploying the interactive web dashboard.
     
## Data Collection Methodology
1. **Web Scraping**: 
- Job listings were scraped from [CareerViet Website](https://careerviet.vn/viec-lam/data-k-vi.html) using Selenium for automated browsing and BeautifulSoup for parsing HTML content.
- Extracted fields include job title, company name, location, salary, experience requirements, and job descriptions.

                    
2. **Data Cleaning**: 
- Standardized date formats and salary ranges for consistency.
- Transformed experience requirements into a structured format.
- Removed duplicate listings and handled missing values.
- Filter out irrelevant job listings from web scraping results.

                    
3. **Skills Extraction**:
- Automatically identified and categorized **soft skills**, **hard skills**, and **industry domains** from job descriptions using keyword matching techniques.

                    
4. **Data Analysis**:
- Filtered and segmented data to focus on data-related roles.
- Analyzed trends in job postings over time, salary distributions, required experience levels, high in demand skills, and key hiring companies.

## Execution
The analysis pipeline is controlled by [main.py](https://github.com/phuongtrinhsmile2307/Job-Scraping/blob/main/main.py), which orchestrates the entire workflow:

1. **Web Scraping**: [src/scraper.py](https://github.com/phuongtrinhsmile2307/Job-Scraping/blob/main/src/scraper.py) provides web scraping functionality to collect job listings from CareerViet. The data is saved in the `data/raw/` directory with `careerviet_jobs.csv` file. 

2. **Data Processing**:
   * [data_processing/cleaning.py](https://github.com/phuongtrinhsmile2307/Job-Scraping/blob/main/data_processing/cleaning.py) handles data cleaning, standardization, and filtering. The data is saved in `data/processed`directory with 2 files: 
     * `processed_data.csv`: all jobs after cleaning
     * `filtered_data.csv`: only data related jobs after filter for irrelevant jobs
   * [data_processing/transformation.py](https://github.com/phuongtrinhsmile2307/Job-Scraping/blob/main/data_processing/transformation.py) performs skill extraction and categorization. The processed data is saved in the data/processed with:
     * `analyst_jobs.csv`: only 'analyst' jobs with skill extraction


3. **Visualization**: [visualization/plots.py](https://github.com/phuongtrinhsmile2307/Job-Scraping/blob/main/visualization/plots.py) contains functions to create various visualizations of the job market data, which are saved to the `results/figures/` directory.

4. **Configuration**: [setting.py](https://github.com/phuongtrinhsmile2307/Job-Scraping/blob/main/config/setting.py) contains global settings and parameters for the pipeline.

5. **Web Application**: Deploy Streamlit app using [app.py](https://github.com/phuongtrinhsmile2307/Job-Scraping/blob/main/app.py) for interactive visualization of the analysis results.

## Usage

Run the main script with appropriate flags to execute specific parts of the pipeline:

```bash
python main.py --all                # Run entire pipeline
python main.py --scrape             # Only scrape new data
python main.py --clean              # Only clean existing data
python main.py --analyze            # Only analyze cleaned data
python main.py --visualize          # Only create visualizations
```

The processed data and visualizations can be found in the `data/processed/` and `results/figures/` directories, respectively.
