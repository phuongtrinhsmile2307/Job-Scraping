"""
Data Transformation Module

This module handles advanced transformations for job data analysis,
particularly focusing on skills extraction.
"""
import re
import pandas as pd
from collections import Counter
from typing import List, Dict, Set, Optional, Union, Tuple
import warnings

# Suppress specific warning related to Google Translate API
warnings.filterwarnings("ignore", message="Locale detection in Google Translate has been migrated")
warnings.filterwarnings("ignore", message="Falling back to the python implementation of the service")

class SkillsExtractor:
    """Class for extracting skills from job descriptions and requirements."""
    
    def __init__(self, use_translator=True):
        """
        Initialize the skills extractor.
        
        Args:
            use_translator: Whether to use translation for non-English text
        """
        self.use_translator = use_translator
        self.translator = None
        
        if use_translator:
            try:
                from googletrans import Translator
                self.translator = Translator()
            except ImportError:
                print("Google Translate not available. Install with: pip install googletrans==4.0.0-rc1")
                self.use_translator = False
        
        # Initialize skill dictionaries
        self.soft_skills = self._load_soft_skills()
        self.hard_skills = self._load_hard_skills()
        self.domains = self._load_domains()
        
        # Convert to lowercase for case-insensitive matching
        self.soft_skills_lower = {skill.lower(): skill for skill in self.soft_skills}
        self.hard_skills_lower = {skill.lower(): skill for skill in self.hard_skills}
        self.domains_lower = {skill.lower(): skill for skill in self.domains}
    
    def _load_soft_skills(self) -> List[str]:
        """Load the list of soft skills."""
        return [
            "Accountability", "Adaptability", "Adaptability in Change", "Active Learning",
            "Analytical Thinking", "Attention To Detail", "Building Rapport", "Business Acumen",
            "Change Management", "Coaching", "Cognitive Flexibility", "Collaboration", "Compassion",
            "Communication", "Conflict Management", "Conflict Mediation", "Conflict Prevention",
            "Conflict Resolution", "Consensus Building", "Creativity", "Critical Decision Making",
            "Critical Observation", "Critical Thinking", "Cross-Cultural", "Cultural Awareness",
            "Cultural Sensitivity", "Curiosity", "Customer Service", "Customer Retention",
            "Customer-Centric Mindset","Clarity", "Data-Driven", "Decision Making", "Delegation",
            "Diplomacy", "Diversity and Inclusion Awareness", "Effective Delegation",
            "Emotional Intelligence", "Emotional Regulation", "Empathy", "Empowerment",
            "Enthusiasm", "Ethical Judgment", "Facilitation", "Fast Learner",
            "Fast Problem Assessment", "Feedback Incorporation", "Flexibility", "Focus",
            "Giving and Receiving Feedback", "Goal Setting", "Grit", "Growth Mindset",
            "Handling Criticism","Humility","Kindness", "Influencing", "Initiative","Imagination", "Insight Generation",
            "Innovation", "Interpersonal","Inclusivity","Intuition", "Leadership", "Listening", "Logical Reasoning",
            "Mentoring", "Mindfulness", "Motivational", "Negotiation", "Networking",
            "Open-Mindedness", "Optimism","Optimistic Thinking", "Ownership Mentality", "Patience",
            "People Management", "Persuasion", "Positive Attitude", "Presentation","Precision",
            "Problem Sensitivity", "Problem-Framing", "Problem-Solving","Perseverance", "Process Improvement",
            "Process Optimization", "Professionalism", "Public Speaking", "Relationship Building",
            "Relationship Maintenance", "Reliability", "Resilience", "Resourcefulness",
            "Risk Management", "Scenario Planning", "Self-Awareness", "Self-Confidence",
            "Self-Discipline", "Self-Learning", "Self-Motivation", "Self-Reflection", "Sensitivity",
            "Situational Awareness", "Stakeholder Management", "Storytelling", "Spontaneity",
            "Strategic Thinking", "Stress Management", "Synthesizing Information",
            "Systems Thinking", "Task Prioritization", "Team Building", "Time Management",
            "Tolerance", "Trustworthiness", "Transparency", "Visionary Thinking", "Work Ethic",
            "Work-Life Balance"
        ]
        
    def translate_text(self, text: str) -> str:
        """
        Translate Vietnamese text to English if detected.
        
        Args:
            text: Text to translate
            
        Returns:
            Translated text or original if translation fails/not needed
        """
        if pd.isna(text) or not text:
            return ""
        
        if not self.use_translator or not self.translator:
            return text
        
        try:
            detected_lang = self.translator.detect(text).lang
            if detected_lang == "vi":  # If text is in Vietnamese, translate it
                return self.translator.translate(text, src="vi", dest="en").text
        except Exception as e:
            print(f"Translation error: {e}")
        
        return text  # Return original if not Vietnamese or translation fails
    
    def extract_skills(self, text: str, skill_dict: Dict[str, str]) -> List[str]:
        """
        Extract and count skills from text.
        
        Args:
            text: Text to extract skills from
            skill_dict: Dictionary of skills to search for
            
        Returns:
            List of found skills
        """
        if pd.isna(text) or not text:
            return []
        
        # Translate if needed
        processed_text = self.translate_text(text).lower()
        found_skills = []
        
        # Use regex with word boundaries to find whole-word matches
        for skill_lower, skill_original in skill_dict.items():
            matches = re.findall(rf'\b{re.escape(skill_lower)}\b', processed_text)
            found_skills.extend([skill_original] * len(matches))
        
        return found_skills
    
    def extract_all_skills(self, df: pd.DataFrame, text_column: str = "Job Requirements") -> pd.DataFrame:
        """
        Extract all types of skills from a text column in the DataFrame.
        
        Args:
            df: DataFrame containing job data
            text_column: Column containing text to extract skills from
            
        Returns:
            DataFrame with additional columns for extracted skills
        """
        # Make a copy to avoid modifying the original
        result_df = df.copy()
        
        # Add translated column if translator is available
        if self.use_translator and self.translator:
            result_df["Translated " + text_column] = result_df[text_column].apply(self.translate_text)
            source_column = "Translated " + text_column
        else:
            source_column = text_column
        
        # Extract skills
        result_df["Soft Skills"] = result_df[source_column].apply(
            lambda x: self.extract_skills(x, self.soft_skills_lower)
        )
        
        result_df["Hard Skills"] = result_df[source_column].apply(
            lambda x: self.extract_skills(x, self.hard_skills_lower)
        )
        
        result_df["Domains"] = result_df[source_column].apply(
            lambda x: self.extract_skills(x, self.domains_lower)
        )
        
        return result_df
    
    def get_skills_counts(self, df: pd.DataFrame, skills_column: str) -> pd.DataFrame:
        """
        Get counts of skills from a skills column.
        
        Args:
            df: DataFrame with extracted skills
            skills_column: Column containing lists of skills
            
        Returns:
            DataFrame with skills counts sorted by frequency
        """
        # Flatten and count occurrences
        all_skills = [skill for skills_list in df[skills_column] for skill in skills_list]
        skill_counts = Counter(all_skills)
        
        # Convert to DataFrame for visualization
        return pd.DataFrame(skill_counts.items(), columns=["Skill", "Count"]).sort_values(
            by="Count", ascending=False
        )

    def _load_hard_skills(self) -> List[str]:
        """Load the list of hard skills."""
        hard_skills = []
        
        # Business Intelligence & Data Visualization
        hard_skills.extend([
            "Amazon QuickSight", "Business Intelligence Tools", "Dashboard",
            "Data Democratization", "Data Storytelling", "Data Visualization", "Domo", 
            "Embedded Analytics", "Figma", "Google Data Studio", "Looker", "Metric Design", 
            "Metabase", "MicroStrategy", "Mode Analytics", "Power BI", "PowerPoint", 
            "Qlik Sense", "QlikView", "Report", "Self-Service BI", "Sisense", "Tableau", 
            "ThoughtSpot", "TIBCO Spotfire", "Zoho Analytics", "JIRA", "Confluence"
        ])
        
        # Business & Market Analysis
        hard_skills.extend([
            "Asset Valuation", "Business Process Improvement", "Churn Prediction",
            "Cohort Analysis", "Consumer Behavior Analysis", "Credit Risk Modeling",
            "Customer Lifetime Value", "Customer Segmentation", "Data-Driven Decision Making",
            "Econometric Modeling", "Financial Forecasting", "Financial Modeling",
            "Financial Risk Management", "Market Research", "Marketing Mix Modeling",
            "Portfolio Optimization", "Predictive Modeling", "Pricing Strategy",
            "Procurement Analytics", "Product Analytics", "Risk Assessment", "Ad-hoc"
        ])
        
        # Statistics & Analytics
        hard_skills.extend([
            "A/B Testing", "Anomaly Detection", "Bayesian Inference", "Causal Inference",
            "Chi-Square Testing", "Cluster Analysis", "Decision Trees", "Descriptive Statistics",
            "Exploratory Data Analysis", "EDA", "Factor Analysis", "Funnel Analysis",
            "Hypothesis Testing", "Statistics", "K-Means", "Latent Variable Modeling", 
            "Mathematics", "Metric Design", "Monte Carlo Simulation", "Multivariate Analysis", 
            "Nonparametric Statistics", "Panel Data Analysis", "Predictive Analytics", 
            "Problem-Framing", "Quantitative Research", "Regression Analysis", "SEM", 
            "Sentiment Analysis", "SPSS", "Statistical Analysis", "Statistical Inference", 
            "Statistical Modeling", "Structural Equation Modeling", "Survival Analysis", 
            "Time Series Analysis"
        ])
        
        # Database & Data Engineering
        hard_skills.extend([
            "Amazon Athena", "Apache Airflow", "Apache Druid", "Apache Flink",
            "Apache Hive", "Apache NiFi", "Apache Pinot", "Azure Synapse Analytics",
            "BigQuery", "Cassandra", "Change Data Capture", "ClickHouse",
            "CockroachDB", "Data Blending", "Data Cleaning", "Data Engineering",
            "Data Governance", "Data Integration", "Data Management", "Data Mart",
            "Data Mining", "Data Modeling", "Data Orchestration", "Data Pipeline Development",
            "Data Quality Management", "Data Warehousing", "Database Management",
            "Delta Lake", "Dremio", "ETL", "Fivetran", "Google Bigtable", "Graph Database",
            "Greenplum", "Hadoop", "HDFS", "IBM", "IBM Db2", "Kafka", "MariaDB",
            "MongoDB", "MySQL", "Neo4j", "NoSQL", "OLAP", "OLTP",
            "PostgreSQL", "Presto", "Redshift", "SAP HANA", "Snowflake", "Spark SQL",
            "SQL", "SQLite", "Starburst", "Trino", "Vertica"
        ])
        
        # Cloud & DevOps
        hard_skills.extend([
            "AWS", "Azure", "Bitbucket", "CI/CD Pipelines", "Data Pipeline",
            "Cloud Computing", "Cloud Data Warehousing", "Cloud Security",
            "Continuous Deployment", "Continuous Integration", "Databricks",
            "DataOps", "DevOps", "Docker", "Docker Swarm", "FinOps", "Git",
            "GitHub", "GitLab", "Google Cloud Platform", "Helm", "Hybrid Cloud",
            "Istio", "Jenkins", "Kubernetes", "Microservices", "Multi-Cloud",
            "Serverless Computing", "Terraform", "Terraform Cloud", "Vertex AI"
        ])
        
        # AI & Machine Learning
        hard_skills.extend([
            "AI Ethics", "AutoML", "Bayesian Optimization", "ChatGPT", "Computer Vision",
            "Deep Learning", "Feature Engineering", "Federated Learning", "Generative AI",
            "Hugging Face", "Keras", "Large Language Models", "LangChain",
            "Machine Learning", "MLOps", "Natural Language Processing", "NLP",
            "Neural Networks", "Predictive Analytics", "PyCaret", "PyTorch",
            "Reinforcement Learning", "Scikit-Learn", "Self-Supervised Learning",
            "TensorFlow", "Transformer Models", "Vector Databases", "XGBoost",
            "LightGBM", "Stable Diffusion", "Object Detection"
        ])
        
        # Automation & Scripting
        hard_skills.extend([
            "Airflow", "Alteryx", "Ansible", "Apache NiFi", "Automation",
            "AutoHotkey", "Bash", "Excel", "Google Analytics", "Google Sheet",
            "IBM Watson", "Informatica", "JMP", "Knime", "Macros",
            "Matlab", "Matplotlib", "Operational Research", "Pandas", "Pipeline",
            "Powershell", "Process Mining", "Python", "Python Automation",
            "R", "RPA", "Robotic Process Automation", "SAS", "Scipy",
            "Scrape", "Scraping", "Scripting", "SEO Optimization",
            "Shell Scripting", "Task Scheduling", "VBA", "Web Scraping",
            "Workflow Automation", "Power Automate"
        ])
        
        # ERP, CRM & Business Systems
        hard_skills.extend([
            "CRM", "ERP", "HubSpot CRM", "Microsoft Dynamics 365", "NetSuite",
            "Oracle ERP", "SAP", "Salesforce", "Workday"
        ])
        
        # Additional categories
        hard_skills.extend([
            # Cybersecurity & Compliance
            "Cloud Security", "Cryptography", "Cybersecurity", "Data Privacy Engineering",
            "Ethical Hacking", "GDPR Compliance", "IAM", "Identity Access Management",
            "Penetration Testing", "Security Information and Event Management", "SIEM",
            "SOC 2 Compliance", "SOC Compliance", "Threat Intelligence",
            "Zero Trust Security", "Zero-Day Exploits",
            
            # Supply Chain & Operations
            "Demand Forecasting", "Lean Six Sigma", "Logistics Analytics",
            "Network Optimization", "Operations Research", "Process Mapping",
            "Smart Warehousing", "Supply Chain Analytics",
            
            # Software Development & Optimization
            "Algorithms", "Code Optimization", "Code Profiling",
            "Concurrency Control", "Embedded Systems", "Julia",
            "Low-Code/No-Code Development", "Optimization",
            "Parallel Computing", "Perl", "Process Optimization",
            "Rust", "Scala", "Software Development Life Cycle", "SDLC",
            "Test-Driven Development",
            
            # Web & Marketing Analytics
            "Adobe Analytics", "Attribution Modeling", "Customer Journey Analytics",
            "Facebook Pixel", "Google Tag Manager", "Heatmap Analysis",
            "Marketing Analytics", "Programmatic Advertising", "Scraping",
            "Tag Management", "Web Analytics",
            
            # Advanced Computing & Security
            "Edge Computing", "Fog Computing", "Homomorphic Encryption", "IoT",
            "Quantum Cryptography", "Real-Time Analytics"
        ])
        
        return hard_skills
    
    def _load_domains(self) -> List[str]:
        """Load the list of industry domains."""
        return [
            "3D Printing", "Accounting", "Actuarial Science", "Advertising", "Aerospace", 
            "Agribusiness", "Agriculture", "Alternative Medicine", "Animal Science", 
            "Anthropology", "Apparel", "Aquaculture", "Archaeology", "Architecture",
            "Artificial Intelligence", "Audit", "Asset Management", "Astronomy", 
            "Astrophysics", "Athletics", "Audio Engineering", "Augmented Reality", 
            "Automotive", "Aviation", "Banking", "Behavioral Science", "Bioinformatics", 
            "Biometrics", "Biotechnology", "Blockchain", "Broadcasting", "Call Center", 
            "Chemical Engineering", "Cinematography", "Cloud Computing", "Coaching", 
            "Cognitive Science", "Commercial Real Estate", "Compliance",
            "Construction", "Consulting", "Consumer Goods", "Corporate Finance", 
            "Cryptocurrency", "Culinary Arts", "Cybersecurity", "Dairy", "Dentistry", 
            "Digital Marketing", "Drone Technology", "Ecommerce", "Econometrics", 
            "Economic Policy", "Education", "Elder Care", "Electric Vehicles",
            "Electrical Engineering", "Electronics", "Embedded Systems", 
            "Emergency Management", "Energy", "Entertainment", "Environmental Science", 
            "Ethical Hacking", "Event Management", "Fashion", "Finance", "Fire Safety", 
            "Fitness", "FMCG", "Food Science", "Forensic Science", "Forestry", "Fraud Detection",
            "Fulfillment", "Gaming", "Genetics", "Geology", "Geospatial", "Glass", "Government",
            "Green Energy", "Healthcare", "Health Economics", "Health Informatics", 
            "Health Policy", "History", "Home Improvement", "Hospitality", "Human Resources", 
            "HR", "Human Rights", "Immunology", "Industrial Automation", "Industrial Design", 
            "Industrial Engineering", "Information Security", 
            "Infrastructure", "Insurance", "Interior Design", "Inventory", "Journalism", 
            "Labor Relations", "Landscape Architecture", "Law", "Library Science", "Linguistics", 
            "Logistics", "Luxury Goods", "Machine Learning", "Manufacturing", "Marine Biology", 
            "Marine Shipping", "Marketing", "Materials Science", "Mechanical Engineering", 
            "Media", "Medical", "Meteorology", "Microbiology", "Military Strategy", "Mining", 
            "Mobile App", "Molecular Biology", "Music", "Nanotechnology", "Neurology",
            "Neuroscience", "Nonprofit", "Nuclear Energy", "Nutritional Science", 
            "Occupational Therapy", "Oil & Gas", "Operations Management", "Optometry", 
            "Paper", "Pathology", "Performing Arts", "Personal Finance", "Petroleum Engineering", 
            "Pharmaceutical", "Philanthropy", "Photography", "Physics", "Physiotherapy", 
            "Political Science", "Printing", "Private Equity", "Product Design",
            "Product Management", "Project Management", "Psychiatry", "Psychology", 
            "Public Administration", "Public Health", "Public Policy", "Public Relations", 
            "Quality Assurance", "Quantum Computing", "Railway", "Real Estate", "Recreation", 
            "Recruitment", "Rehabilitation", "Renewable Energy", "Research", "Retail", 
            "Revenue Generation", "Risk Management", "Robotics", "Satellite Communications",
            "Security", "Sales", "Semiconductors", "SEO", "Social Media", "Social Work", 
            "Sociology", "Solar Power", "Supply Chain", "Sustainable Development", 
            "Taxation", "Tax", "Technology", "Telecommunications", "Textiles", "Tourism", 
            "Transportation", "Urban Planning", "Utilities", "Venture Capital", "Veterinary", 
            "Virtual Reality", "Waste Management", "Water Management", "Web Analytics",
            "Wellness", "Wholesale", "Wildlife Conservation", "Wind Energy", "Zoology"
        ]