"""
Project Settings

Configuration settings for the Vietnamese Job Market Analysis project.
"""
import os
from pathlib import Path

# Project structure
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
RESULTS_DIR = PROJECT_ROOT / 'results'

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, RESULTS_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

# File paths
RAW_DATA_PATH = RAW_DATA_DIR / 'careerviet_jobs.csv'
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / 'processed_data.csv'
FILTERED_DATA_PATH = PROCESSED_DATA_DIR / 'filtered_data.csv'
ANALYST_DATA_PATH = PROCESSED_DATA_DIR / 'analyst_jobs.csv'
ANALYST_SKILL_PATH = PROCESSED_DATA_DIR / 'analyst_skills.csv'
SOFT_SKILL_PATH= PROCESSED_DATA_DIR / 'soft_skills.csv'
HARD_SKILL_PATH = PROCESSED_DATA_DIR / 'hard_skills.csv'
DOMAIN_SKILL_PATH = PROCESSED_DATA_DIR / 'domain_skills.csv'



# Scraper settings
CHROME_DRIVER_PATH = r"C:/Selenium Driver"  # Update with your actual path
CAREERVIET_BASE_URL = "https://careerviet.vn/viec-lam/data-k-vi.html"  # Data jobs
MAX_PAGES = 10
MAX_JOBS = 600
MAX_JOBS_PER_PAGE = 60
MAX_WORKERS = 4

# Data processing settings
USD_TO_VND_RATE = 25505  # Exchange rate

# Visualization settings
VISUALIZATION_STYLE = "whitegrid"
VISUALIZATION_CONTEXT = "paper"
VISUALIZATION_PALETTE = "flare"
SAVE_FIGURES = True
FIGURES_DIR = RESULTS_DIR / 'figures'
FIGURES_DIR.mkdir(exist_ok=True, parents=True)

# Analysis settings
FILTER_DATA_JOBS = True
EXTRACT_SKILLS = True
USE_TRANSLATOR = True

# Job categories to filter
DATA_RELATED_KEYWORDS = [
    'Data', 'Analyst', 'Phân Tích', 'Dữ Liệu', 'Intelligence', 
    'Machine Learning', 'Scientist', 'Công Nghệ', 'Ai', 'Statistics', 'Research',
    'Researcher', 'Ecommerce', 'Digital', 'Nghiên Cứu', 'Crm', 'Erp', 'Sap',
    'System', 'Database', 'Bi', 'Sql', 'Python', 'Etl', 'Insights', 'Analytics',
    'Artificial Intelligence', 'Clustering', 'Regression', 'Dashboard', 'Excel', 
    'Power Bi', 'Visualization', 'Reporting', 'Forecasting', 'Quantitative',
    'Modelling', 'Dự Báo', 'Báo Cáo', 'Mining', 'Analysis', 'Analytic', 'Labeling',
    'Platform', 'Số Liệu', 'Automation', 'Cntt', 'Software Engineer'
]