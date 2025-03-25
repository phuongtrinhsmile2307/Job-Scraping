"""
Main Script for Vietnamese Job Market Analysis

This script runs the entire data pipeline: scraping, cleaning, analyzing, and visualizing job data.
"""
import os
import time
import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from config.setting import (
    RAW_DATA_PATH, PROCESSED_DATA_PATH, FILTERED_DATA_PATH, ANALYST_DATA_PATH,
    CAREERVIET_BASE_URL, MAX_PAGES, MAX_JOBS, MAX_JOBS_PER_PAGE, MAX_WORKERS,
    USD_TO_VND_RATE, CHROME_DRIVER_PATH, FIGURES_DIR, SAVE_FIGURES, ANALYST_SKILL_PATH
)
from src.scraper import CareerVietScraper
from data_processing.cleaning import JobDataCleaner
from data_processing.transformation import SkillsExtractor
from visualization.plots import JobMarketVisualizer

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Vietnamese Job Market Analysis")
    
    parser.add_argument('--scrape', action='store_true', help='Scrape new data')
    parser.add_argument('--clean', action='store_true', help='Clean the data')
    parser.add_argument('--analyze', action='store_true', help='Analyze the data')
    parser.add_argument('--visualize', action='store_true', help='Create visualizations')
    parser.add_argument('--all', action='store_true', help='Run the entire pipeline')
    
    parser.add_argument('--url', type=str, default=CAREERVIET_BASE_URL, 
                        help='Starting URL for job search')
    parser.add_argument('--pages', type=int, default=MAX_PAGES, 
                        help='Maximum number of pages to scrape')
    parser.add_argument('--max-jobs', type=int, default=MAX_JOBS, 
                        help='Maximum total jobs to scrape')
    parser.add_argument('--input', type=str, default=None,
                        help='Input CSV file path (overrides default)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output CSV file path (overrides default)')
    
    return parser.parse_args()

def scrape_data(args):
    """Scrape job data from CareerViet."""
    print("\n" + "="*50)
    print("SCRAPING JOB DATA")
    print("="*50)
    
    start_time = time.time()
    
    # Initialize the scraper
    scraper = CareerVietScraper(
        chrome_driver_path=CHROME_DRIVER_PATH,
        max_workers=MAX_WORKERS,
        max_jobs_per_page=MAX_JOBS_PER_PAGE,
        max_jobs=args.max_jobs
    )
    
    # Scrape the data
    df_scraped = scraper.scrape(args.url, max_pages=args.pages)
    
    # Save the scraped data
    output_path = args.output or RAW_DATA_PATH
    scraper.save_to_csv(df_scraped, output_path)
    
    print(f"\nScraping completed in {time.time() - start_time:.2f} seconds")
    print(f"Scraped {len(df_scraped)} jobs and saved to {output_path}")
    
    return df_scraped

def clean_data(df=None, args=None):
    """Clean and preprocess the job data."""
    print("\n" + "="*50)
    print("CLEANING JOB DATA")
    print("="*50)
    
    start_time = time.time()
    
    # Load data if not provided
    if df is None:
        input_path = args.input or RAW_DATA_PATH
        print(f"Loading data from {input_path}")
        df = pd.read_csv(input_path)
    
    # Initialize the cleaner
    cleaner = JobDataCleaner(exchange_rate=USD_TO_VND_RATE)
    
    # Clean the data
    cleaned_df = cleaner.clean(df)
    
    # Filter data jobs
    filtered_df = cleaner.filter_data_jobs(cleaned_df)

    # Filter data analyst jobs
    analyst_df = cleaner.filter_analyst_jobs(cleaned_df)

    # Save the processed data
    cleaned_df.to_csv(PROCESSED_DATA_PATH, index=False)
    filtered_df.to_csv(FILTERED_DATA_PATH, index=False)
    analyst_df.to_csv(ANALYST_DATA_PATH, index=False)
    
    print(f"\nCleaning completed in {time.time() - start_time:.2f} seconds")
    print(f"Processed {len(cleaned_df)} jobs and saved to {PROCESSED_DATA_PATH}")
    print(f"Filtered {len(filtered_df)} data-related jobs and saved to {FILTERED_DATA_PATH}")
    print(f"Filtered {len(analyst_df)} analyst-related jobs and saved to {ANALYST_DATA_PATH}")
    
    return filtered_df, analyst_df
    

def analyze_data(df=None, args=None):
    """Analyze the job data by extracting skills."""
    print("\n" + "="*50)
    print("ANALYZING JOB DATA")
    print("="*50)
    
    start_time = time.time()
    
    # Load data if not provided
    if df is None:
        input_path = args.input or ANALYST_DATA_PATH
        print(f"Loading data from {input_path}")
        df = pd.read_csv(input_path)
    
    # Initialize the skills extractor
    skills_extractor = SkillsExtractor(use_translator=True)
    
    # Extract skills
    print("Extracting skills from job requirements...")
    analyst_jobs = skills_extractor.extract_all_skills(df)
    
    # Save the analyzed data
    analyst_jobs.to_csv(ANALYST_SKILL_PATH, index=False)
    
    # Calculate skill statistics
    soft_skill_df = skills_extractor.get_skills_counts(analyst_jobs, "Soft Skills")
    hard_skill_df = skills_extractor.get_skills_counts(analyst_jobs, "Hard Skills")
    domains_df = skills_extractor.get_skills_counts(analyst_jobs, "Domains")
    
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds")
    print(f"Analyzed {len(analyst_jobs)} jobs and saved to {ANALYST_SKILL_PATH}")
    print(f"Found {len(soft_skill_df)} unique soft skills")
    print(f"Found {len(hard_skill_df)} unique hard skills")
    print(f"Found {len(domains_df)} unique domains")
    return soft_skill_df, hard_skill_df, domains_df

def visualize_data(df=None, skills_data=None, args=None):
    """Create visualizations of the job data."""
    print("\n" + "="*50)
    print("CREATING VISUALIZATIONS")
    print("="*50)
    
    start_time = time.time()
    
    # Load data if not provided
    if df is None:
        input_path = args.input or FILTERED_DATA_PATH
        print(f"Loading data from {input_path}")
        df = pd.read_csv(input_path)
        

    # Initialize the visualizer
    visualizer = JobMarketVisualizer()
    
    # Create output directory for figures if saving
    if SAVE_FIGURES:
        os.makedirs(FIGURES_DIR, exist_ok=True)
    
    # Create visualizations
    print("Creating location analysis...")
    visualizer.plot_jobs_by_location(
        df, 
        save_path=FIGURES_DIR/"jobs_by_location.png" if SAVE_FIGURES else None
    )
    
    print("Creating salary analysis...")
    visualizer.plot_salary_by_experience(
        df,
        save_path=FIGURES_DIR/"salary_by_experience.png" if SAVE_FIGURES else None
    )
    
    print("Creating date analysis...")
    visualizer.plot_jobs_by_date(
        df,
        save_path=FIGURES_DIR/"jobs_by_date.png" if SAVE_FIGURES else None
    )
    
    print("Creating job level analysis...")
    visualizer.plot_experience_by_job_level(
        df,
        save_path=FIGURES_DIR/"experience_by_job_level.png" if SAVE_FIGURES else None
    )
    
    print("Creating top job titles analysis...")
    visualizer.plot_top_job_titles(
        df, n=15,
        save_path=FIGURES_DIR/"top_job_titles.png" if SAVE_FIGURES else None
    )
    
    print("Creating top companies analysis...")
    visualizer.plot_top_companies(
        df, n=15,
        save_path=FIGURES_DIR/"top_companies.png" if SAVE_FIGURES else None
    )
    
    print("Creating salary heatmap...")
    visualizer.plot_salary_heatmap(
        df,
        save_path=FIGURES_DIR/"salary_heatmap.png" if SAVE_FIGURES else None
    )
    
    
    # If skills data is provided, create skills visualizations
    if skills_data:
        soft_skill_df, hard_skill_df, domains_df = skills_data
        
        print("Creating skills analysis...")
        visualizer.plot_skills(
            soft_skill_df.head(20), 
            "Top 20 Soft Skills Required", 
            "Blues_r",
            save_path=FIGURES_DIR/"top_soft_skills.png" if SAVE_FIGURES else None
        )
        
        visualizer.plot_skills(
            hard_skill_df.head(20), 
            "Top 20 Hard Skills Required", 
            "Reds_r",
            save_path=FIGURES_DIR/"top_hard_skills.png" if SAVE_FIGURES else None
        )
        
        visualizer.plot_skills(
            domains_df.head(20), 
            "Top 20 Industry Domains", 
            "Greens_r",
            save_path=FIGURES_DIR/"top_domains.png" if SAVE_FIGURES else None
        )
    
    print(f"\nVisualization completed in {time.time() - start_time:.2f} seconds")
    
    if SAVE_FIGURES:
        print(f"Saved figures to {FIGURES_DIR}")

def main():
    """Run the job market analysis pipeline."""
    # Parse command line arguments
    args = parse_args()
    
    # Determine which parts of the pipeline to run
    run_all = args.all
    run_scrape = args.scrape or run_all
    run_clean = args.clean or run_all
    run_analyze = args.analyze or run_all
    run_visualize = args.visualize or run_all
    
    # Track execution time
    start_time = time.time()
    
    # Initialize variables to store data between pipeline stages
    df_scraped = None
    df_filtered = None
    df_analyst = None
    skills_data = None
    
    # Run the pipeline
    if run_scrape:
        df_scraped = scrape_data(args)
    
    if run_clean:
        df_filtered, df_analyst = clean_data(df_scraped, args)
    
    if run_analyze:
        soft_skill_df, hard_skill_df, domains_df = analyze_data(df_analyst, args)
        skills_data = (soft_skill_df, hard_skill_df, domains_df)
    
    if run_visualize:
        skills_data=analyze_data(df_analyst, args)
        visualize_data(df_filtered, skills_data, args)
    
    # Print execution summary
    total_time = time.time() - start_time
    print("\n" + "="*50)
    print(f"PIPELINE COMPLETED in {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    print("="*50)

if __name__ == "__main__":
    main()