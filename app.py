import streamlit as st
import pandas as pd
from pathlib import Path
import ast
import plotly.express as px
import plotly.graph_objs as go
from collections import Counter
from plotly.subplots import make_subplots
import random

# Set page configuration
st.set_page_config(
    page_title="Vietnamese Data Job Market Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define paths
DATA_DIR = Path("data/processed")
FIGURES_DIR = Path("results/figures")

# Custom CSS with modern styling
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
""", unsafe_allow_html=True)


CUSTOM_CSS = """
<style>
@keyframes revealText {
    from {
        background-size: 0% 100%;
    }
    to {
        background-size: 100% 100%;
    }
}
/* Main header with gradient */
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    font-family: "Inter", sans-serif;
    background: linear-gradient(to right, #07efeb, #1ec4dc, #369acd, #4d6fbe, #6644af);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-repeat: no-repeat;
    background-size: 100% 100%;
    animation: revealText 1.5s ease-out forwards;
    text-align: left;
    display: inline-block;
}

/* Section headers */
.section-header {
    font-size: 1.5rem;
    font-weight: bold;
    font-family: "Inter", sans-serif;
    color: #3d5169; 
    padding-top: 1rem;
    margin-bottom: 1rem;
}
.subsection-header {
    font-size: 1.3rem;
    font-family: "Inter", sans-serif;
    color: #506278; 
    padding-top: 0.5rem;
}

/* Category tags */
.category-label {
    display: inline-block;
    padding: 4px 8px;
    margin: 3px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-family: "Inter", sans-serif;
    background-color: #eaecef;
    color: #506278;
}
.category-label:hover {
    background-color: #d0d7de;
}

/* About section on overview page */
.about-section {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 20px;
    height: 100%;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    border: 1px solid rgba(0,0,0,0.03);
}
.about-section h2 {
    color: #3d5169;
    margin-bottom: 15px;
    font-family: "Inter", sans-serif;
    font-size: 1.5rem;
}
.about-section p, .about-section ul {
    color: #506278;
    margin-bottom: 15px;
    font-family: "Inter", sans-serif;
}

/* Metric cards */
.metric-container {
    background-color: white;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    height: 100px;
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 20px;
    text-align: left;
}
.metric-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
}  
.metric-value-container {
    display: flex;
    align-items: center;
    gap: 10px;
}  
.metric-icon {
    font-size: 28px;
    opacity: 0.9;
}     
.metric-title {
    font-weight: 500;
    color: #757982;
    font-family: "Inter", sans-serif;
    font-size: 14px;
}
.metric-value {
    font-size: 24px;
    font-family: "Inter", sans-serif;
    color: 	#113768;
    font-weight: bold;
} 
/* Custom color gradient for icons */
.container-1 .metric-icon { color: #07efeb; }
.container-2 .metric-icon { color: #1ec4dc; }
.container-3 .metric-icon { color: #369acd; }
.container-4 .metric-icon { color: #4d6fbe; }
.container-5 .metric-icon { color: #6644af; } 

.metric-card {
    background-color: white;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    text-align: center;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.metric-card .value {
    font-size: 2rem;
    font-weight: bold;
    font-family: "Inter", sans-serif;
    color: #113768;
    margin-bottom: 5px;
}
.metric-card .label {
    color: #757982;
    font-size: 0.9rem;
    font-family: "Inter", sans-serif;
}

/* Modern tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;

}
.stTabs [data-baseweb="tab"] {
    height: 40px;
    border-radius: 8px;
    padding: 0 16px;
    background-color: #f8f9fa;
}
.stTabs [aria-selected="true"] {
    background-color: #f0f7fe !important;
    color: #1E293B !important;
}


/* Filter section */
.filter-section {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 20px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

/* Custom card styling */
div.card-container {
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    overflow: hidden;
    padding-bottom: 15px;
    height: 100%;
    margin-bottom: 20px;
    border: 1px solid rgba(0,0,0,0.05);
    transition: all 0.3s ease;
}

div.card-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 20px rgba(0,0,0,0.12);
    border-color: rgba(54, 154, 205, 0.3);
}

div.card-image {
    width: 100%;
    height: 180px;
    overflow: hidden;
    margin-bottom: 10px;
}

div.card-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

div.card-content h3 {
    padding: 0 15px;
    margin-bottom: 5px;
    color: #3d5169;
    font-family: "Inter", sans-serif;
    font-size: 1.4rem;
}

div.card-content p {
    padding: 0 15px;
    color: #506278;
    font-family: "Inter", sans-serif;
    font-size: 0.9rem;
}
/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #f8f8f8 !important;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Helper function to load data
@st.cache_data
def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Error loading data from {file_path}: {e}")
        return None

# Helper function to convert string representation of lists to actual lists
def convert_string_to_list(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else [])
    return df

# Helper function to count skills
def count_skills(df, skills_column):
    # Flatten the lists of skills and count occurrences
    all_skills = [skill for skills_list in df[skills_column] for skill in skills_list]
    skill_counts = Counter(all_skills)
    
    # Convert to DataFrame for visualization
    skill_df = pd.DataFrame(skill_counts.items(), columns=["Skill", "Count"])
    
    # Sort by count in descending order
    return skill_df.sort_values(by="Count", ascending=False)

# Helper function to create plotly skills chart with improved styling
def plotly_skills_chart(skill_df, title, color_scheme, top_n=20):
    """Create a Plotly bar chart for skills visualization with modern styling"""
    # Take only top N skills
    skill_df_top = skill_df.head(top_n).sort_values(by="Count", ascending=True)
    
    # Create gradient colors based on the scheme
    if color_scheme == "purple":
        colors=['#daceeb', '#b59ed8', '#8f70c3', '#6644af']
    elif color_scheme == "mint":
        colors = ['#a8e7fb', '#80caeb', '#59aedb', '#3391cb', '#0074b9']
    else:
        colors = ['#aaebea', '#86c8c7', '#64a6a6', '#418585', '#1a6666']
    
    fig = px.bar(
        skill_df_top, 
        x="Count", 
        y="Skill",
        orientation='h',
        title=title,
        color="Count",
        color_continuous_scale=colors,
        text="Count"
    )
    
    fig.update_layout(
        height=600,
        template='plotly_white',
        title_font_size=16,
        title_font_family="Inter, sans-serif",
        xaxis_title="Frequency",
        yaxis_title="Skills",
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Inter, sans-serif"
        )
    )
    
    fig.update_traces(
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
    )
    
    return fig

def plot_top_job_titles(job_title_counts):
    """Create a Plotly bar chart for top job titles with improved styling"""
    job_title_counts_top = job_title_counts.nlargest(15).sort_values(ascending=True)
    
    fig = px.bar(
        x=job_title_counts_top.values, 
        y=job_title_counts_top.index, 
        orientation='h',
        title='Top 15 Data-Related Job Titles',
        labels={'x': 'Number of Job Postings', 'y': 'Job Title'},
        color_discrete_sequence=['#9c7fca']
    )
    
    fig.update_layout(
        height=500,
        template='plotly_white',
        title_font_size=16,
        title_font_family="Inter, sans-serif",
        xaxis_title_font_size=12,
        yaxis_title_font_size=12,
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Inter, sans-serif"
        )
    )
    
    fig.update_traces(
        texttemplate='%{x}', 
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Job Postings: %{x}<extra></extra>'
    )
    
    return fig

def plot_job_postings_over_time(jobs_by_date):
    """Create a Plotly line chart for job postings over time with improved styling"""
    try:
        # Format dates to show only day and month
        jobs_by_date['Date'] = pd.to_datetime(jobs_by_date['Date'])
        jobs_by_date['FormattedDate'] = jobs_by_date['Date'].dt.strftime('%d-%b')
        
        fig = px.line(
            jobs_by_date, 
            x='FormattedDate', 
            y='JobCount', 
            title='Job Postings By Date',
            labels={'FormattedDate': 'Date', 'JobCount': 'Number of Job Postings'},
            markers=True,
            line_shape='linear',
            color_discrete_sequence=['#60e5f7']
        )
        
        # Add area under the line
        fig.add_trace(
            go.Scatter(
                x=jobs_by_date['FormattedDate'],
                y=jobs_by_date['JobCount'],
                fill='tozeroy',
                fillcolor='rgba(54, 154, 205, 0.1)',
                line=dict(color='rgba(0,0,0,0)'),
                showlegend=False,
                hoverinfo='skip'
            )
        )
        
        # Ensure all dates are shown on x-axis
        fig.update_xaxes(
            tickmode='array', 
            tickvals=jobs_by_date['FormattedDate'],
            tickangle=270
        )
        
        fig.update_layout(
            height=500,
            template='plotly_white',
            title_font_size=16,
            title_font_family="Inter, sans-serif",
            xaxis_title_font_size=12,
            yaxis_title_font_size=12,
            margin=dict(b=100, l=10, r=10, t=50),
            plot_bgcolor="white",
            paper_bgcolor="white",
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Inter, sans-serif"
            )
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Jobs: %{y}<extra></extra>'
        )
        
        return fig
    except Exception as e:
        # Create a simple error message figure
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text=f"Error creating chart: {e}",
            font=dict(color="red", size=14),
            showarrow=False,
            xref="paper", yref="paper"
        )
        fig.update_layout(height=300)
        return fig
def plot_job_postings_by_day(jobs_by_day):
    """Create a Plotly column chart for job postings by day of the week with improved styling"""
    try:
        # Define the days of the week in order
        days_order = ['Monday', 'Tuesday', 'Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # If your data doesn't have the days in the right order, you can reindex it
        if 'Day' in jobs_by_day.columns:
            jobs_by_day = jobs_by_day.set_index('Day').reindex(days_order).reset_index()
        
        fig = px.bar(
            jobs_by_day, 
            y='Day', 
            x='JobCount', 
            title='Job Postings by Day of Week',
            labels={'Day': 'Day of Week', 'JobCount': 'Number of Job Postings'},
            color_discrete_sequence=['#9c7fca'],
            category_orders={"Day": days_order}  # Ensure correct order
        )
        
        # Update the layout for better appearance
        fig.update_layout(
            height=500,
            template='plotly_white',
            title_font_size=16,
            title_font_family="Inter, sans-serif",
            xaxis_title_font_size=12,
            yaxis_title_font_size=12,
            margin=dict(b=100, l=10, r=10, t=50),
            plot_bgcolor="white",
            paper_bgcolor="white",
            bargap=0.25,
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Inter, sans-serif"
            )
        )
        
        # Add data labels on top of bars
        fig.update_traces(
            texttemplate='%{x}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Jobs: %{y}<extra></extra>'
        )
        
        # Remove gridlines
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False, rangemode="tozero")
        
        return fig
    except Exception as e:
        # Create a simple error message figure
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text=f"Error creating chart: {e}",
            font=dict(color="red", size=14),
            showarrow=False,
            xref="paper", yref="paper"
        )
        fig.update_layout(height=300)
        return fig
def plot_location_distribution(location_counts):
    """Create an interactive Plotly bar chart for location distribution with improved styling"""
    
    # Sort the data by number of jobs in descending order
    location_counts_sorted = location_counts.sort_values('Number of Jobs', ascending=False)
    
    fig = px.bar(
        location_counts_sorted, 
        x='Number of Jobs', 
        y='Location',
        orientation='h',
        title='Data-Related Jobs by Location',
        color='Number of Jobs',
        color_discrete_sequence=px.colors.sequential.Blues[-4:],
        text='Number of Jobs'
    )
    
    fig.update_layout(
        height=500,
        template='plotly_white',
        title_font_size=16,
        title_font_family="Inter, sans-serif",
        xaxis_title="Number of Jobs",
        yaxis_title="Location",
        yaxis={'categoryorder': 'total ascending'},
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Inter, sans-serif"
        )
    )
    
    fig.update_traces(
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Jobs: %{x}<extra></extra>'
    )
    
    return fig
def create_vietnam_province_map(filtered_jobs):
    """
    Create an interactive province-level map visualization of Vietnam
    that shows job distribution across all provinces and major cities
    """
    
    # Define Vietnam provinces with coordinates
    vietnam_provinces = {
        # Northern Vietnam
        "Hà Nội": [21.0285, 105.8542],
        "Hải Phòng": [20.8449, 106.6881],
        "Thái Nguyên": [21.5942, 105.8480],
        "Bắc Ninh": [21.1861, 106.0763],
        "Hạ Long": [20.9515, 107.0748],
        "Lào Cai": [22.4855, 103.9757],
        "Điện Biên": [21.3856, 103.0321],
        "Hải Dương": [20.9373, 106.3145],
        "Nam Định": [20.4345, 106.1680],
        "Ninh Bình": [20.2478, 105.9743],
        "Vĩnh Phúc": [21.3608, 105.5474],
        "Cao Bằng": [22.6666, 106.2639],
        "Lạng Sơn": [21.8531, 106.7608],
        "Bắc Giang": [21.2717, 106.1947],
        "Thái Bình": [20.4462, 106.3366],
        "Hà Giang": [22.8025, 104.9784],
        "Yên Bái": [21.7226, 104.9096],
        "Phú Thọ": [21.4219, 105.2245],
        "Tuyên Quang": [21.7767, 105.2280],
        "Hà Nam": [20.5835, 105.9241],
        "Bắc Kạn": [22.1477, 105.8347],
        "Hưng Yên": [20.6546, 106.0569],
        "Hòa Bình": [20.8172, 105.3380],
        "Quảng Ninh": [21.0064, 107.2925],
        "Sơn La": [21.1018, 103.7289],
        
        # Central Vietnam
        "Đà Nẵng": [16.0544, 108.2022],
        "Huế": [16.4637, 107.5909],
        "Nha Trang": [12.2388, 109.1968],
        "Quy Nhơn": [13.7829, 109.2196],
        "Đà Lạt": [11.9404, 108.4583],
        "Thanh Hóa": [19.8068, 105.7852],
        "Nghệ An": [19.2339, 104.9200],
        "Hà Tĩnh": [18.3559, 105.8877],
        "Quảng Bình": [17.4682, 106.6004],
        "Quảng Trị": [16.7943, 107.0451],
        "Thừa Thiên Huế": [16.4637, 107.5909],
        "Quảng Nam": [15.5394, 108.0191],
        "Quảng Ngãi": [15.1213, 108.7953],
        "Bình Định": [13.7829, 109.2196],
        "Phú Yên": [13.0881, 109.0928],
        "Khánh Hòa": [12.2388, 109.1968],
        "Ninh Thuận": [11.6739, 108.8629],
        "Bình Thuận": [10.9336, 108.1001],
        "Kon Tum": [14.3539, 108.0095],
        "Gia Lai": [13.9808, 108.2218],
        "Đắk Lắk": [12.6704, 108.0372],
        "Đắk Nông": [12.0040, 107.6874],
        "Lâm Đồng": [11.9404, 108.4583],
        
        # Southern Vietnam
        "Hồ Chí Minh": [10.8231, 106.6297],
        "Cần Thơ": [10.0452, 105.7469],
        "Biên Hòa": [10.9513, 106.8226],
        "Vũng Tàu": [10.3460, 107.0843],
        "Long Xuyên": [10.3864, 105.4351],
        "Tây Ninh": [11.3598, 106.1108],
        "Bình Phước": [11.7512, 106.7235],
        "Bình Dương": [11.3254, 106.4772],
        "Đồng Nai": [10.9513, 106.8226],
        "Bà Rịa - Vũng Tàu": [10.3460, 107.0843],
        "Long An": [10.5446, 106.4121],
        "Tiền Giang": [10.3639, 106.3638],
        "Bến Tre": [10.2433, 106.3759],
        "Trà Vinh": [9.9513, 106.3346],
        "Vĩnh Long": [10.2538, 105.9722],
        "Đồng Tháp": [10.4937, 105.6882],
        "An Giang": [10.3864, 105.4351],
        "Kiên Giang": [10.0187, 105.1629],
        "Cần Thơ": [10.0452, 105.7469],
        "Hậu Giang": [9.7579, 105.6404],
        "Sóc Trăng": [9.6037, 105.9736],
        "Bạc Liêu": [9.2929, 105.7275],
        "Cà Mau": [9.1769, 105.1521]
    }
    
    # Define regions for color coding
    province_regions = {
        # Northern provinces
        "Hà Nội": "North",
        "Hải Phòng": "North",
        "Thái Nguyên": "North",
        "Bắc Ninh": "North",
        "Hạ Long": "North",
        "Lào Cai": "North",
        "Điện Biên": "North",
        "Hải Dương": "North",
        "Nam Định": "North",
        "Ninh Bình": "North",
        "Vĩnh Phúc": "North",
        "Cao Bằng": "North",
        "Lạng Sơn": "North",
        "Bắc Giang": "North",
        "Thái Bình": "North",
        "Hà Giang": "North",
        "Yên Bái": "North",
        "Phú Thọ": "North",
        "Tuyên Quang": "North",
        "Hà Nam": "North",
        "Bắc Kạn": "North",
        "Hưng Yên": "North",
        "Hòa Bình": "North",
        "Quảng Ninh": "North",
        "Sơn La": "North",
        
        # Central provinces
        "Đà Nẵng": "Central",
        "Huế": "Central",
        "Nha Trang": "Central",
        "Quy Nhơn": "Central",
        "Đà Lạt": "Central",
        "Thanh Hóa": "Central",
        "Nghệ An": "Central",
        "Hà Tĩnh": "Central",
        "Quảng Bình": "Central",
        "Quảng Trị": "Central",
        "Thừa Thiên Huế": "Central",
        "Quảng Nam": "Central",
        "Quảng Ngãi": "Central",
        "Bình Định": "Central",
        "Phú Yên": "Central",
        "Khánh Hòa": "Central",
        "Ninh Thuận": "Central",
        "Bình Thuận": "Central",
        "Kon Tum": "Central",
        "Gia Lai": "Central",
        "Đắk Lắk": "Central",
        "Đắk Nông": "Central",
        "Lâm Đồng": "Central",
        
        # Southern provinces
        "Hồ Chí Minh": "South",
        "Cần Thơ": "South",
        "Biên Hòa": "South",
        "Vũng Tàu": "South",
        "Long Xuyên": "South",
        "Tây Ninh": "South",
        "Bình Phước": "South",
        "Bình Dương": "South",
        "Đồng Nai": "South",
        "Bà Rịa - Vũng Tàu": "South",
        "Long An": "South",
        "Tiền Giang": "South",
        "Bến Tre": "South",
        "Trà Vinh": "South",
        "Vĩnh Long": "South",
        "Đồng Tháp": "South",
        "An Giang": "South",
        "Kiên Giang": "South",
        "Hậu Giang": "South",
        "Sóc Trăng": "South",
        "Bạc Liêu": "South",
        "Cà Mau": "South"
    }
    
    # Extract location counts
    location_counts = filtered_jobs['Location'].value_counts().reset_index()
    location_counts.columns = ['Location', 'Jobs']
    
    # Process job data by location
    location_data = []
    
    # Function to extract all provinces from a location string
    def extract_provinces(location_str):
        found_provinces = []
        
        # Sort provinces by length (descending) to match longer names first 
        # (prevents partial matches like matching "Hà" in "Hà Nội")
        sorted_provinces = sorted(vietnam_provinces.keys(), key=len, reverse=True)
        
        # Clone the location string for processing
        remaining_text = location_str.lower()
        
        # Try to find all provinces in the location string
        for province in sorted_provinces:
            if province.lower() in remaining_text:
                found_provinces.append(province)
                # Remove the matched province from the string to prevent double counting
                remaining_text = remaining_text.replace(province.lower(), "")
        
        return found_provinces
    
    # Process each location
    for idx, row in location_counts.iterrows():
        location = row['Location']
        jobs = row['Jobs']
        
        # Extract all provinces from the location string
        provinces = extract_provinces(location)
        
        # If multiple provinces found, add the full job count to each province
        if len(provinces) > 1:
            for province in provinces:
                coords = vietnam_provinces[province]
                region = province_regions[province]
                
                # Add small random offset to avoid overlapping points in the same province
                offset = 0.02
                lat = coords[0] + random.uniform(-offset, offset)
                lon = coords[1] + random.uniform(-offset, offset)
                
                location_data.append({
                    'Location': location,
                    'Province': province,
                    'Region': region,
                    'Jobs': jobs,  # Full job count for each province
                    'Latitude': lat,
                    'Longitude': lon
                })
        else:
            # Single province found
            province = provinces[0]
            coords = vietnam_provinces[province]
            region = province_regions[province]
            
            # Add small random offset to avoid overlapping points in the same province
            offset = 0.02
            lat = coords[0] + random.uniform(-offset, offset)
            lon = coords[1] + random.uniform(-offset, offset)
            
            location_data.append({
                'Location': location,
                'Province': province,
                'Region': region,
                'Jobs': jobs,
                'Latitude': lat,
                'Longitude': lon
            })
    
    # Create DataFrame for locations
    df_locations = pd.DataFrame(location_data)
    
    # Calculate province job totals
    province_job_totals = df_locations.groupby('Province')['Jobs'].sum().reset_index()
    province_job_totals = province_job_totals.sort_values('Jobs', ascending=False)
    
    # Create the map figure
    fig = go.Figure()
    
    # Define region colors
    region_colors = {
        "North": "#8df5f2",
        "Central": "#edeb88",
        "South": "#9c7fca"
    }
    
    
    # Improve marker sizing to be more proportional to job count
    min_jobs = df_locations['Jobs'].min()
    max_jobs = df_locations['Jobs'].max()
    
    # Use a logarithmic scale for better visualization when job counts vary widely
    # Ensure minimum bubble size is visible but max size doesn't overwhelm the map
    min_size, max_size = 10, 40
    
    # Function to scale marker size using square root scaling for better visual representation
    def scale_marker_size(jobs):
        if max_jobs == min_jobs:  # Prevent division by zero
            return (min_size + max_size) / 2
        else:
            # Square root scaling provides a more balanced visual representation
            scale_factor = (jobs / max_jobs) ** 0.5  # Square root scaling
            return min_size + scale_factor * (max_size - min_size)
    
    # Add province markers with job counts by region
    for region in ["North", "Central", "South"]:
        # Filter locations for this region
        region_df = df_locations[df_locations['Region'] == region]
        
        if not region_df.empty:
            # Calculate scaled sizes for each marker
            sizes = region_df['Jobs'].apply(scale_marker_size)
            
            # Add markers for each province with job data
            fig.add_trace(go.Scattermapbox(
                lat=region_df['Latitude'],
                lon=region_df['Longitude'],
                mode='markers',
                marker=dict(
                    size=sizes,
                    color=region_colors[region],
                    opacity=0.8,
                    sizemode='diameter'
                ),
                text=region_df.apply(lambda x: f"{x['Province']} ({x['Location']}): {round(x['Jobs'])} jobs", axis=1),
                name=f"{region} Provinces",
                hoverinfo='text'
            ))
    
    # Configure the map
    fig.update_layout(
        autosize=True,
        hovermode='closest',
        height=700,
        mapbox=dict(
            style="carto-positron",
            zoom=5,
            center=dict(lat=16.0, lon=107.0)  # Center of Vietnam
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.5,
            xanchor="right",
            x=1
        )
    )
    
    # Add region view buttons
    buttons = [
        dict(
            args=[{"mapbox.center": {"lat": 21.0, "lon": 105.8}, "mapbox.zoom": 6}],
            label="North Vietnam",
            method="relayout"
        ),
        dict(
            args=[{"mapbox.center": {"lat": 16.0, "lon": 108.0}, "mapbox.zoom": 6}],
            label="Central Vietnam",
            method="relayout"
        ),
        dict(
            args=[{"mapbox.center": {"lat": 10.8, "lon": 106.6}, "mapbox.zoom": 6}],
            label="South Vietnam",
            method="relayout"
        ),
        dict(
            args=[{"mapbox.center": {"lat": 16.0, "lon": 107.0}, "mapbox.zoom": 5}],
            label="Full Vietnam",
            method="relayout"
        )
    ]
    
    fig.update_layout(
        updatemenus=[dict(
            type="buttons",
            direction="right",
            buttons=buttons,
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.315,
            xanchor="center",
            y=1.1,
            yanchor="top"
        )]
    )
    
    return fig


def display_province_job_statistics(filtered_jobs):
    """
    Display detailed province job statistics with tables and charts
    using improved province extraction logic
    """
    
    # Define Vietnam provinces with their regions
    vietnam_regions = {
        # Northern provinces
        "Hà Nội": "North",
        "Hải Phòng": "North",
        "Thái Nguyên": "North",
        "Bắc Ninh": "North",
        "Hạ Long": "North",
        "Lào Cai": "North",
        "Điện Biên": "North",
        "Hải Dương": "North",
        "Nam Định": "North",
        "Ninh Bình": "North",
        "Vĩnh Phúc": "North",
        "Cao Bằng": "North",
        "Lạng Sơn": "North",
        "Bắc Giang": "North",
        "Thái Bình": "North",
        "Hà Giang": "North",
        "Yên Bái": "North",
        "Phú Thọ": "North",
        "Tuyên Quang": "North",
        "Hà Nam": "North",
        "Bắc Kạn": "North",
        "Hưng Yên": "North",
        "Hòa Bình": "North",
        "Quảng Ninh": "North",
        "Sơn La": "North",
        
        # Central provinces
        "Đà Nẵng": "Central",
        "Huế": "Central",
        "Nha Trang": "Central",
        "Quy Nhơn": "Central",
        "Đà Lạt": "Central",
        "Thanh Hóa": "Central",
        "Nghệ An": "Central",
        "Hà Tĩnh": "Central",
        "Quảng Bình": "Central",
        "Quảng Trị": "Central",
        "Thừa Thiên Huế": "Central",
        "Quảng Nam": "Central",
        "Quảng Ngãi": "Central",
        "Bình Định": "Central",
        "Phú Yên": "Central",
        "Khánh Hòa": "Central",
        "Ninh Thuận": "Central",
        "Bình Thuận": "Central",
        "Kon Tum": "Central",
        "Gia Lai": "Central",
        "Đắk Lắk": "Central",
        "Đắk Nông": "Central",
        "Lâm Đồng": "Central",
        
        # Southern provinces
        "Hồ Chí Minh": "South",
        "Cần Thơ": "South",
        "Biên Hòa": "South",
        "Vũng Tàu": "South",
        "Long Xuyên": "South",
        "Tây Ninh": "South",
        "Bình Phước": "South",
        "Bình Dương": "South",
        "Đồng Nai": "South",
        "Bà Rịa - Vũng Tàu": "South",
        "Long An": "South",
        "Tiền Giang": "South",
        "Bến Tre": "South",
        "Trà Vinh": "South",
        "Vĩnh Long": "South",
        "Đồng Tháp": "South",
        "An Giang": "South",
        "Kiên Giang": "South",
        "Hậu Giang": "South",
        "Sóc Trăng": "South",
        "Bạc Liêu": "South",
        "Cà Mau": "South"
    }
    
    # Extract location counts
    location_counts = filtered_jobs['Location'].value_counts().reset_index()
    location_counts.columns = ['Location', 'Jobs']
    
    # Function to extract all provinces from a location string
    def extract_provinces(location_str):
        found_provinces = []
        
        # Sort provinces by length (descending) to match longer names first
        # (prevents partial matches like matching "Hà" in "Hà Nội")
        sorted_provinces = sorted(vietnam_regions.keys(), key=len, reverse=True)
        
        # Clone the location string for processing
        remaining_text = location_str.lower()
        
        # Try to find all provinces in the location string
        for province in sorted_provinces:
            if province.lower() in remaining_text:
                found_provinces.append(province)
                # Remove the matched province from the string to prevent double counting
                remaining_text = remaining_text.replace(province.lower(), "")
        
        return found_provinces
    
    # Process job data by location
    location_data = []
    
    # Process each location
    for idx, row in location_counts.iterrows():
        location = row['Location']
        jobs = row['Jobs']
        
        # Extract all provinces from the location string
        provinces = extract_provinces(location)
        
        # If multiple provinces found, add the full job count to each province
        if len(provinces) > 1:
            for province in provinces:
                region = vietnam_regions[province]
                
                location_data.append({
                    'Location': location,
                    'Province': province,
                    'Region': region,
                    'Jobs': jobs  # Full job count for each province
                })
        else:
            # Single province found
            province = provinces[0]
            region = vietnam_regions[province]
            
            location_data.append({
                'Location': location,
                'Province': province,
                'Region': region,
                'Jobs': jobs
            })
    
    # Create DataFrame for locations
    df_locations = pd.DataFrame(location_data)
    
    # Calculate province job totals and region totals
    province_job_totals = df_locations.groupby('Province')['Jobs'].sum().reset_index()
    province_job_totals = province_job_totals.sort_values('Jobs', ascending=False)
    
    region_job_totals = df_locations.groupby('Region')['Jobs'].sum().reset_index()
    
    # Create region color map for consistent colors
    region_colors = {
        "North": "#8df5f2",
        "Central": "#edeb88",
        "South": "#9c7fca"
    }
    
    # Display statistics in tabs
    #tab1, tab2= st.tabs(["Regional Overview", "Province Breakdown"])
    
    #with tab1:
        # Regional pie chart
    region_fig = px.pie(
            region_job_totals,
            values='Jobs',
            names='Region',
            title='Job Distribution by Region',
            color='Region',
            color_discrete_map=region_colors,
        )
        
    region_fig.update_layout(
            height=400,
            legend_title="Region",
            font=dict(size=12)
        )
        
    region_fig.update_traces(
            textinfo='percent+label+value',
            hoverinfo='label+percent+value'
        )
        
    st.plotly_chart(region_fig, use_container_width=True)
    
    #with tab2:
    # Top provinces bar chart
    top_provinces = province_job_totals.head(15)
    # Round the job counts for display
    top_provinces['Jobs'] = top_provinces['Jobs'].round().astype(int)
        
    # Merge with region information
    province_region_map = df_locations[['Province', 'Region']].drop_duplicates()
    top_provinces = pd.merge(top_provinces, province_region_map, on='Province')
        
    province_fig = px.bar(
            top_provinces,
            x='Province',
            y='Jobs',
            color='Region',
            title='Top 15 Provinces by Job Count',
            color_discrete_map=region_colors,
            text='Jobs'
        )
        
    province_fig.update_layout(
            height=500,
            xaxis_title="Province",
            yaxis_title="Number of Jobs",
            xaxis={'categoryorder':'total descending'},
            font=dict(size=12)
        )
        
    province_fig.update_traces(
            texttemplate='%{y}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Jobs: %{y}<extra></extra>'
        )
        
    st.plotly_chart(province_fig, use_container_width=True)
        
    # Show province table
    st.subheader("All Provinces with Job Listings")
    # Round the job counts for display in the table
    display_province_totals = province_job_totals.copy()
    display_province_totals['Jobs'] = display_province_totals['Jobs'].round().astype(int)
    st.dataframe(display_province_totals)
    
    return df_locations


# Integrate these functions into the main app
def display_regional_job_analysis(filtered_jobs):
    """
    Display comprehensive Vietnam province analysis in the dashboard
    """
    import streamlit as st
    
    st.markdown('<div class="section-header">Data-Related Jobs Distribution In Vietnam</div>', unsafe_allow_html=True)
    
    # Create and display the interactive province map
    try:
        map_fig = create_vietnam_province_map(filtered_jobs)
        st.plotly_chart(map_fig, use_container_width=True, config={'displayModeBar': True})
        
    except Exception as e:
        st.error(f"Could not create provincial visualization: {e}")
        st.info("Provincial visualization requires location data in the dataset.")


def overview_page(filtered_jobs, all_jobs, analyst_jobs):
    """
    Display the Overview page with clickable cards instead of buttons
    """
    # Add main header
    st.markdown('<div class="main-header">Vietnamese Data Job Market Analysis</div>', unsafe_allow_html=True)
    st.markdown("""
        This project analyzes job listings from CareerViet, focusing on data-related positions. 
        Explore insights into job distribution, salary trends, required skills, and company hiring patterns.
        """)
    st.markdown("<br>", unsafe_allow_html=True)
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
        
    # Metric 1: Total Jobs
    with col1:
        st.markdown(f"""
        <div class='metric-container container-1'>
            <div class='metric-content'>
                <div class='metric-title'>Total Jobs</div>
                <div class='metric-value-container'>
                    <div class='metric-icon'>
                        <i class='fas fa-briefcase'></i>
                    </div>
                    <div class='metric-value'>{len(all_jobs):,}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Metric 2: Data-Related Jobs
    with col2:
        st.markdown(f"""
        <div class='metric-container container-2'>
            <div class='metric-content'>
                <div class='metric-title'>Data Jobs</div>
                <div class='metric-value-container'>
                    <div class='metric-icon'>
                        <i class='fas fa-laptop-code'></i>
                    </div>
                    <div class='metric-value'>{len(filtered_jobs):,}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Metric 3: Analyst-Related Jobs
    with col3:
        st.markdown(f"""
        <div class='metric-container container-3'>
            <div class='metric-content'>
                <div class='metric-title'>Analyst Jobs</div>
                <div class='metric-value-container'>
                    <div class='metric-icon'>
                        <i class='fas fa-chart-line'></i>
                    </div>
                    <div class='metric-value'>{len(analyst_jobs):,}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Metric 4: Average Min Salary
    with col4:
        st.markdown(f"""
        <div class='metric-container container-4'>
            <div class='metric-content'>
                <div class='metric-title'>Min Salary (VND)</div>
                <div class='metric-value-container'>
                    <div class='metric-icon'>
                        <i class='fas fa-money-bill'></i>
                    </div>
                    <div class='metric-value'>{filtered_jobs['Min_Salary'].mean()/1e6:.1f}M</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Metric 5: Average Max Salary
    with col5:
        st.markdown(f"""
        <div class='metric-container container-5'>
            <div class='metric-content'>
                <div class='metric-title'>Max Salary (VND)</div>
                <div class='metric-value-container'>
                    <div class='metric-icon'>
                        <i class='fas fa-coins'></i>
                    </div>
                    <div class='metric-value'>{filtered_jobs['Max_Salary'].mean()/1e6:.1f}M</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
            
    # Load data
    all_jobs_path = DATA_DIR / "processed_data.csv"
    filtered_jobs_path = DATA_DIR / "filtered_data.csv"
    analyst_jobs_path = DATA_DIR / "analyst_jobs.csv"
    
    all_jobs = load_data(all_jobs_path)
    filtered_jobs = load_data(filtered_jobs_path)
    analyst_jobs = load_data(analyst_jobs_path)
    
    if analyst_jobs is not None:
        analyst_jobs = convert_string_to_list(analyst_jobs, ['Soft Skills', 'Hard Skills', 'Domains'])
    
    # Check if data is loaded successfully
    if filtered_jobs is None:
        st.error("Could not load the filtered jobs data. Please check the data files.")
        return
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Create a layout with left for about section and right for cards
    left_col, right_col = st.columns([4, 6])
    
    # Left column with about section
    with left_col:
        st.markdown("""    
            ### Key Insights
            - Job postings for data-related positions are concentrated in major cities like Ho Chi Minh City and Hanoi.
            - Salary distributions vary significantly based on experience levels and company size.
            - In-demand technical skills include SQL, Python, and Power BI, while soft skills like communication and problem-solving are also frequently mentioned.
            - Emerging trends show a growing demand for data analysts and business intelligence roles in industries such as e-commerce and finance.     
            
            
            ### Data Collection Methodology
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
            - Analyzed trends in job postings, salary distributions, required experience levels, and key hiring companies.

                    
            ### Tools & Technologies
            **Python**:
            - `Selenium`: automated web scraping.
            - `BeautifulSoup`: HTML parsing.
            - `Pandas`: data manipulation and transformation.
            - `Matplotlib`, `Seaborn` & `Plotly`: data visualization.
            - `Streamlit`: building and deploying the interactive web dashboard.
            """) 
    with right_col:
        # Simple two-column layout for cards
        row1_cols = st.columns(2)
        
        # Job Distribution Card - SIMPLEST APPROACH
        with row1_cols[0]:
            # Display image
            st.image("https://images.unsplash.com/photo-1591696205602-2f950c417cb9?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", 
                    use_container_width=True)
            
            # Add button below image
            if st.button("**Job Distribution**", key="job_dist_btn", use_container_width=True):
                st.session_state.page = "Job Distribution"
                st.rerun()
        
        # Salary Analysis Card
        with row1_cols[1]:
            # Display image
            st.image("https://images.pexels.com/photos/10972831/pexels-photo-10972831.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2", 
                    use_container_width=True)
            
            # Add button below image
            if st.button("**Salary Analysis**", key="salary_btn", use_container_width=True):
                st.session_state.page = "Salary Analysis"
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

        # Second row of cards
        row2_cols = st.columns(2)

        # Skills Analysis Card
        with row2_cols[0]:
            # Display image
            st.image("https://www.splunk.com/content/dam/splunk-blogs/images/en_us/2023/06/data-scientist-role.jpg", 
                    use_container_width=True)
            
            # Add button below image
            if st.button("**Skills Analysis**", key="skills_btn", use_container_width=True):
                st.session_state.page = "Skills Analysis"
                st.rerun()
        
        # Company Analysis Card
        with row2_cols[1]:
            # Display image
            st.image("https://images.pexels.com/photos/164572/pexels-photo-164572.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
                    use_container_width=True)
            
            # Add button below image
            if st.button("**Company Analysis**", key="company_btn", use_container_width=True):
                st.session_state.page = "Company Analysis"
                st.rerun()
        
       
        display_regional_job_analysis(filtered_jobs)
        
        
# Updated Job Distribution Page function
def job_distribution_page(filtered_jobs):
    """
    Display the Job Distribution Analysis page with improved styling and interactivity
    """
    st.markdown('<div id="job-distribution-section" class="section-header">Job Distribution Analysis</div>', unsafe_allow_html=True)

    try:
        # Data preparation


        # Create layout with tabs
        tab1, tab2, tab3 = st.tabs(["Job Postings Over Time", "Geographic Distribution", "Job Titles"])
        
        with tab1:
            try:
                filtered_jobs['Date'] = pd.to_datetime(filtered_jobs['Date'], errors='coerce')
                # Remove any NaT values that might cause issues
                date_df = filtered_jobs.dropna(subset=['Date'])
                # Group by date for the time series
                jobs_by_date = date_df.groupby(date_df['Date'].dt.date).size().reset_index(name='JobCount')
                # Group by day of week for the column chart
                date_df['Day'] = date_df['Date'].dt.strftime('%A')  # Get day name
                jobs_by_day = date_df.groupby('Day').size().reset_index(name='JobCount')

                # Generate and display the time series and day by day column chart
                if not jobs_by_date.empty:
                    time_series_fig = plot_job_postings_over_time(jobs_by_date)
                    st.plotly_chart(time_series_fig, use_container_width=True, config={'displayModeBar': True})
                    st.markdown(f"""- The data shows **{jobs_by_date['JobCount'].max() if not jobs_by_date.empty else 'N/A'}** postings on the busiest day.""")
    
                    # Add a small space between charts
                    st.markdown("<br>", unsafe_allow_html=True)

                if not jobs_by_day.empty:
                    max_day_count = jobs_by_day['JobCount'].max()
                    max_day = jobs_by_day.loc[jobs_by_day['JobCount'] == max_day_count, 'Day'].iloc[0]
                    min_day_count = jobs_by_day['JobCount'].min()
                    min_day = jobs_by_day.loc[jobs_by_day['JobCount'] == min_day_count, 'Day'].iloc[0]
                    
                    # Generate and display the day of week column chart
                    day_chart_fig = plot_job_postings_by_day(jobs_by_day)
                    st.plotly_chart(day_chart_fig, use_container_width=True, config={'displayModeBar': True})

                    # Display insights
                    st.markdown(f"""
                    - **{max_day}** has the most job postings with **{max_day_count}** listings
                    - **{min_day}** has the fewest job postings with **{min_day_count}** listings
                    """)
                else:
                    st.warning("Not enough date data to create the charts.")
            except Exception as e:
                st.error(f"Error creating charts: {e}")
        
        with tab2:
            display_province_job_statistics(filtered_jobs)

        with tab3:
            # Create and display the job titles chart
            try:
                job_title_counts = filtered_jobs['Job Title'].value_counts()
                if not job_title_counts.empty:
                    job_titles_fig = plot_top_job_titles(job_title_counts)
                    st.plotly_chart(job_titles_fig, use_container_width=True, config={'displayModeBar': True})
                    st.markdown(f"""
                    - **Most Common Job Title**: "{job_title_counts.index[0]}" is the most common job title with {job_title_counts.values[0]} listings
                    """)
                else:
                    st.warning("Not enough job title data to create the chart.")
            except Exception as e:
                st.error(f"Error creating job titles chart: {e}")


    except Exception as e:
        st.error(f"An error occurred while analyzing job distribution: {e}")
        st.info("Please check your data files and try refreshing the page.")

# Updated Salary Analysis Page function
def salary_analysis(filtered_jobs):
    """
    Display the Salary Analysis page with improved styling and interactivity
    """
    st.markdown('<div id="salary-analysis-section" class="section-header">Salary Analysis</div>', unsafe_allow_html=True)
    
    min_salary = int(filtered_jobs['Min_Salary'].min() / 1e6)
    max_salary = int(filtered_jobs['Max_Salary'].max() / 1e6 + 1)
    
    # Improved slider with better styling
    salary_range = st.slider(
        "Salary Range (Million VND)",
        min_value=min_salary,
        max_value=max_salary,
        value=(min_salary, max_salary),
        step=1
    )
    
    # Filter data based on salary range
    filtered_by_salary = filtered_jobs[
        (filtered_jobs['Min_Salary'] >= salary_range[0] * 1e6) & 
        (filtered_jobs['Max_Salary'] <= salary_range[1] * 1e6)
    ]
    
    st.markdown(
    f'<div style="text-align: right;">Showing {len(filtered_by_salary)} jobs within selected salary range</div>',
    unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Create tabs for different salary analyses
    tab1, tab2, tab3 = st.tabs(["Salary Distribution", "Salary by Experience", "Salary by Location"])
    
    with tab1:
        try:
            # Convert to millions for better readability
            salary_data = filtered_by_salary[['Min_Salary', 'Max_Salary']] / 1e6
            salary_data.columns = ['Min Salary (M VND)', 'Max Salary (M VND)']
            
            # Create two separate histograms with improved styling
            fig = go.Figure()
            
            # Min Salary histogram
            fig.add_trace(go.Histogram(
                x=salary_data['Min Salary (M VND)'], 
                name='Min Salary',
                opacity=1,
                marker_color='#8df5f2',
                bingroup='group1'
            ))
            
            # Max Salary histogram
            fig.add_trace(go.Histogram(
                x=salary_data['Max Salary (M VND)'], 
                name='Max Salary',
                opacity=1,
                marker_color='#9c7fca',
                bingroup='group2'
            ))
            
            # Configure the layout with modern styling
            fig.update_layout(
                title="Salary Distribution (Million VND)",
                xaxis_title="Salary (Million VND)",
                yaxis_title="Number of Jobs",
                yaxis=dict(showgrid=True, gridcolor="#eeeeee", gridwidth=0.1),
                barmode='group',
                bargap=0.1,
                height=500,
                template='plotly_white',
                legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1),
                margin=dict(l=10, r=10, t=50, b=10),
                plot_bgcolor="white",
                paper_bgcolor="white",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Inter, sans-serif"
                )
            )
            
            fig.update_traces(
                hovertemplate='<b>%{x:.1f}M VND</b><br>Jobs: %{y}<extra></extra>'
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        except Exception as e:
            st.error(f"Error creating salary distribution chart: {e}")
            
    with tab2:
        try:
            # Calculate average salary by experience level
            exp_salary = filtered_by_salary.groupby('exp_min').agg({
                'Min_Salary': 'mean',
                'Max_Salary': 'mean'
            }).reset_index()
            
            # Convert to millions
            exp_salary['Min_Salary'] = exp_salary['Min_Salary'] / 1e6
            exp_salary['Max_Salary'] = exp_salary['Max_Salary'] / 1e6
            
            # Create line plot with Plotly and improved styling
            fig_exp = go.Figure()
            
            # Add min salary line
            fig_exp.add_trace(go.Scatter(
                x=exp_salary['exp_min'], 
                y=exp_salary['Min_Salary'], 
                mode='lines+markers',
                name='Min Salary',
                line=dict(color='#07efeb', width=3),
                marker=dict(size=7, color='#07efeb')
            ))
            
            # Add max salary line
            fig_exp.add_trace(go.Scatter(
                x=exp_salary['exp_min'], 
                y=exp_salary['Max_Salary'], 
                mode='lines+markers',
                name='Max Salary',
                line=dict(color='#6644af', width=3),
                marker=dict(size=7, color='#6644af')
            ))
            
            fig_exp.update_layout(
                title="Average Salary by Minimum Experience Required",
                xaxis_title="Minimum Experience (Years)",
                yaxis=dict(showgrid=True, gridcolor="#eeeeee", gridwidth=0.1),
                yaxis_title="Salary (Million VND)",
                height=500,
                template='plotly_white',
                legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1),
                margin=dict(l=10, r=10, t=50, b=10),
                plot_bgcolor="white",
                paper_bgcolor="white",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Inter, sans-serif"
                )
            )
            
            fig_exp.update_traces(
                hovertemplate='<b>%{x} Years</b><br>Salary: %{y:.1f}M VND<extra></extra>'
            )
            
            st.plotly_chart(fig_exp, use_container_width=True, config={'displayModeBar': True})
        except Exception as e:
            st.error(f"Error creating salary by experience chart: {e}")
    
    with tab3:
        try:
            # Group by Location and exp_min, then get the mean salary
            heatmap_data = filtered_by_salary.groupby(['Location', 'exp_min'])['Min_Salary'].mean().reset_index()
            
            # Convert to millions
            heatmap_data['Min_Salary'] /= 1e6
            
            # Get top 5 locations by job count
            top_locations = filtered_by_salary['Location'].value_counts().nlargest(5).index.tolist()
            
            # Filter heatmap data for top locations
            heatmap_data_filtered = heatmap_data[heatmap_data['Location'].isin(top_locations)]
            
            if not heatmap_data_filtered.empty:
                # Pivot the data
                heatmap_pivot = heatmap_data_filtered.pivot(
                    index='exp_min', 
                    columns='Location', 
                    values='Min_Salary'
                )
                
                # Replace NaN with 0 to avoid errors
                heatmap_pivot = heatmap_pivot.fillna(0)
                
                # Create heatmap with improved styling
                fig_heatmap = px.imshow(
                    heatmap_pivot,
                    labels=dict(x="Location", y="Minimum Experience (Years)", color="Salary (M VND)"),
                    x=heatmap_pivot.columns,
                    y=heatmap_pivot.index,
                    color_continuous_scale=['#ffffff', '#a8e7fb', '#3391cb'],
                    aspect="auto",
                    text_auto='.1f'
                )
                
                fig_heatmap.update_layout(
                    title="Average Minimum Salary (Million VND) by Location and Experience",
                    height=600,
                    template='plotly_white',
                    margin=dict(l=10, r=10, t=130, b=10),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    xaxis=dict(
                        title="Location",
                        title_standoff=20,  # Adds spacing
                        side="top"  # Moves x-axis title to the top
                    ),
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=12,
                        font_family="Inter, sans-serif"
                    )
                )
                
                fig_heatmap.update_traces(
                    hovertemplate='<b>%{x}</b><br>Experience: %{y} years<br>Salary: %{z:.1f}M VND<extra></extra>'
                )
                
                st.plotly_chart(fig_heatmap, use_container_width=True, config={'displayModeBar': True})
            else:
                st.info("Not enough data to create a salary heatmap by location and experience")
        except Exception as e:
            st.error(f"Error creating salary heatmap: {e}")
            
            # Provide a simpler alternative
            st.write("Showing alternative salary by location view:")
            
            try:
                # Calculate average salary by location (simpler view)
                loc_salary = filtered_by_salary.groupby('Location').agg({
                    'Min_Salary': 'mean',
                    'Max_Salary': 'mean'
                }).reset_index()
                
                # Convert to millions and take top 5 locations
                loc_salary['Min_Salary'] = loc_salary['Min_Salary'] / 1e6
                loc_salary['Max_Salary'] = loc_salary['Max_Salary'] / 1e6
                loc_salary = loc_salary.sort_values('Min_Salary', ascending=False).head(5)
                
                # Create bar chart with improved styling
                fig_loc = px.bar(
                    loc_salary,
                    x='Location',
                    y=['Min_Salary', 'Max_Salary'],
                    title="Average Salary by Location (Top 5)",
                    labels={'value': 'Salary (Million VND)', 'variable': 'Salary Type'},
                    barmode='group',
                    color_discrete_map={
                        'Min_Salary': '#2196F3',
                        'Max_Salary': '#FFB07C'
                    }
                )
                
                fig_loc.update_layout(
                    height=500,
                    template='plotly_white',
                    legend_title_text='',
                    margin=dict(l=10, r=10, t=50, b=10),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=12,
                        font_family="Inter, sans-serif"
                    )
                )
                
                fig_loc.update_traces(
                    hovertemplate='<b>%{x}</b><br>%{data.name}: %{y:.1f}M VND<extra></extra>'
                )
                
                st.plotly_chart(fig_loc, use_container_width=True, config={'displayModeBar': True})
            except Exception as e2:
                st.error(f"Error creating alternative salary chart: {e2}")
    
    # Insights section
    st.markdown("### Key Insights on Salary")
    st.markdown(f"""
    - **Average Salary Range**: The average job posting offers between {filtered_jobs['Min_Salary'].mean()/1e6:.1f}M and {filtered_jobs['Max_Salary'].mean()/1e6:.1f}M VND
    - **Experience Impact**: Each additional year of experience correlates with approximately {(filtered_jobs['Max_Salary'].max()/1e6 - filtered_jobs['Min_Salary'].min()/1e6)/(filtered_jobs['exp_max'].max() - filtered_jobs['exp_min'].min()):.1f}M VND increase in salary
    - **Location Impact**: Top locations offer salary premiums of up to 20-30% compared to the average
    """)
    st.markdown('</div>', unsafe_allow_html=True)

def skills_analysis_page(analyst_jobs):
    """
    Display the Skills Analysis page with improved styling and interactivity
    Now directly loads skills data from CSV files
    """
    st.markdown('<div id="skills-analysis-section" class="section-header">Skills Analysis</div>', unsafe_allow_html=True)
    st.markdown("""Analysis of only '**Analyst**' Job Postings""")

    SOFT_SKILL_PATH= DATA_DIR/ "soft_skills.csv"
    HARD_SKILLS_PATH= DATA_DIR/ "hard_skills.csv"
    DOMAIN_SKILLS_PATH= DATA_DIR/ "domain_skills.csv"
    
    # Load skills data from CSVs
    soft_skill_df = load_data(SOFT_SKILL_PATH)
    hard_skill_df = load_data(HARD_SKILLS_PATH)
    domains_df = load_data(DOMAIN_SKILLS_PATH)
    
    # Check if skills data is available
    if soft_skill_df.empty and hard_skill_df.empty and domains_df.empty:
        st.error("Skills data is not available. Please check the data files.")
        return
        
    # Create tabs for different skill types
    tab1, tab2, tab3 = st.tabs(["Hard Skills", "Soft Skills", "Industry Domains"])
    
    with tab1:

        # Number of skills to show
        n_skills = st.slider("Number of top hard skills to display", 5, min(30, len(hard_skill_df)), 
                            min(20, len(hard_skill_df)), key="hard_skills_slider")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Plot hard skills using Plotly with improved styling
        if not hard_skill_df.empty:
            fig = plotly_skills_chart(hard_skill_df, f"Top {n_skills} Hard Skills Required", "purple", n_skills)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        else:
            st.info("No hard skills data available.")
        
    with tab2:
        
        # Number of skills to show
        n_skills = st.slider("Number of top soft skills to display", 5, min(30, len(soft_skill_df)), 
                            min(20, len(soft_skill_df)), key="soft_skills_slider")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Plot soft skills using Plotly with improved styling
        if not soft_skill_df.empty:
            fig = plotly_skills_chart(soft_skill_df, f"Top {n_skills} Soft Skills Required", "mint", n_skills)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        else:
            st.info("No soft skills data available.")
        
    
    with tab3:
        
        # Number of domains to show
        n_domains = st.slider("Number of top domains to display", 5, min(30, len(domains_df)), 
                             min(20, len(domains_df)), key="domains_slider")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Plot domains using Plotly with improved styling
        if not domains_df.empty:
            fig = plotly_skills_chart(domains_df, f"Top {n_domains} Industry Domains", "greens", n_domains)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        else:
            st.info("No domain data available.")
        
    # Insights section - now using the CSV data directly
    top_hard_skill = hard_skill_df.iloc[0]['Skill'] if not hard_skill_df.empty else "N/A"
    top_hard_count = hard_skill_df.iloc[0]['Count'] if not hard_skill_df.empty else 0
    
    top_soft_skill = soft_skill_df.iloc[0]['Skill'] if not soft_skill_df.empty else "N/A"
    top_soft_count = soft_skill_df.iloc[0]['Count'] if not soft_skill_df.empty else 0
    
    top_domain = domains_df.iloc[0]['Skill'] if not domains_df.empty else "N/A"
    top_domain_count = domains_df.iloc[0]['Count'] if not domains_df.empty else 0
    
    # Top 3 hard skills
    top3_hard = hard_skill_df.head(3)['Skill'].tolist() if not hard_skill_df.empty else ["N/A"]
    top3_soft = soft_skill_df.head(3)['Skill'].tolist() if not soft_skill_df.empty else ["N/A"]

    st.markdown("### Key Insights on Skills")
    st.markdown(f"""
    - **Most In-Demand Hard Skill**: "{top_hard_skill}" is mentioned in {top_hard_count} job postings
    - **Most In-Demand Soft Skill**: "{top_soft_skill}" is mentioned in {top_soft_count} job postings
    - **Top Industry Domain**: "{top_domain}" is mentioned in {top_domain_count} job postings
    - **Skill Combination**: Jobs frequently require a mix of technical skills ({', '.join(top3_hard)}) and soft skills ({', '.join(top3_soft)})
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Updated Company Analysis Page function
def company_analysis_page(filtered_jobs):
    """
    Display the Company Analysis page with improved styling and interactivity
    """
    st.markdown('<div id="company-analysis-section" class="section-header">Company Analysis</div>', unsafe_allow_html=True)
    
    try:
        # Get top companies
        company_counts = filtered_jobs['Company'].value_counts().nlargest(15)
        
        # Create tabs for different analyses
        tab1, tab2 = st.tabs(["Top Companies", "Company Details"])
        
        with tab1:
            
            # Use a gradient color scale for companies with improved styling
            fig = px.bar(
                x=company_counts.values, 
                y=company_counts.index, 
                orientation='h',
                title="Top 15 Companies Hiring for Data-Related Positions",
                labels={'x': 'Number of Job Postings', 'y': 'Company'},
                color=company_counts.values,
                color_continuous_scale=['#d4f8f6', '#79a3e4', '#6644af'],
                text=company_counts.values
            )
            fig.update_layout(
                height=600,
                template='plotly_white',
                yaxis={'categoryorder': 'total ascending'},
                coloraxis_showscale=False,
                title_font_family="Inter, sans-serif",
                title_font_size=16,
                margin=dict(l=10, r=10, t=50, b=10),
                plot_bgcolor="white",
                paper_bgcolor="white",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Inter, sans-serif"
                )
            )
            fig.update_traces(
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Job Postings: %{x}<extra></extra>'
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        
        with tab2:
            st.markdown('<div class="subsection-header">Company Details</div>', unsafe_allow_html=True)
            
            # Select a company to analyze
            selected_company = st.selectbox(
                "Select a company to analyze",
                options=company_counts.index.tolist()
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Filter jobs for selected company
            company_jobs = filtered_jobs[filtered_jobs['Company'] == selected_company]

            # Company statistics with modern metric cards
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="value">{len(company_jobs)}</div>
                    <div class="label">Job Postings</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="value">{company_jobs['Min_Salary'].mean()/1e6:.1f}M</div>
                    <div class="label">Avg Min Salary (VND)</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="value">{company_jobs['Max_Salary'].mean()/1e6:.1f}M</div>
                    <div class="label">Avg Max Salary (VND)</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Add space 
            st.markdown("<br>", unsafe_allow_html=True)

            
            # Job titles at company
            company_titles = company_jobs['Job Title'].value_counts()
                
            # Create job titles chart with Plotly and improved styling
            if len(company_titles) > 0:
                title_fig = px.bar(
                    x=company_titles.values, 
                    y=company_titles.index, 
                    orientation='h',
                    title=f"Job Titles at {selected_company}",
                    labels={'x': 'Number of Job Postings', 'y': 'Job Title'},
                    color=company_titles.values,
                    color_discrete_sequence=['#8f74bd'],
                    text=company_titles.values
                )
                title_fig.update_layout(
                    height=500,
                    template='plotly_white',
                    yaxis={'categoryorder': 'total ascending'},
                    coloraxis_showscale=False,
                    title_font_family="Inter, sans-serif",
                    title_font_size=16,
                    margin=dict(l=10, r=10, t=50, b=10),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=12,
                        font_family="Inter, sans-serif"
                    )
                )
                title_fig.update_traces(
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Job Postings: %{x}<extra></extra>'
                )
                    
                st.plotly_chart(title_fig, use_container_width=True, config={'displayModeBar': True})
            else:
                st.write(f"No job titles data available for {selected_company}")
            
            # Prepare data for box plot
            company_exp = pd.melt(
                company_jobs[['Job Title', 'exp_min', 'exp_max']], 
                id_vars=['Job Title'], 
                value_vars=['exp_min', 'exp_max'],
                var_name='Experience Type', 
                value_name='Years'
            )
                
            # Create box plot with Plotly and improved styling
            exp_fig = px.box(
                company_exp, 
                x='Experience Type', 
                y='Years',
                title=f"Experience Requirements at {selected_company}",
                color='Experience Type',
                color_discrete_map={'exp_min': '#78f2ef', 'exp_max': '#8f70c3'},
                points="all"
            )
            exp_fig.update_layout(
                height=500,
                template='plotly_white',
                title_font_family="Inter, sans-serif",
                title_font_size=16,
                showlegend=False,
                margin=dict(l=10, r=10, t=50, b=10),
                plot_bgcolor="white",
                paper_bgcolor="white",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Inter, sans-serif"
                )
            )
            exp_fig.update_traces(
                hovertemplate='<b>%{data.name}</b><br>Years: %{y}<extra></extra>'
            )
                
            st.plotly_chart(exp_fig, use_container_width=True, config={'displayModeBar': True})

            # Insights
            st.markdown("### Key Insights for Selected Company")
            st.markdown(f"""
            - **Company Overview**: {selected_company} has {len(company_jobs)} job postings with salaries ranging from {company_jobs['Min_Salary'].mean()/1e6:.1f}M to {company_jobs['Max_Salary'].mean()/1e6:.1f}M VND
            - **Most Common Job**: The most common position is "{company_titles.index[0] if len(company_titles) > 0 else 'N/A'}" ({company_titles.values[0] if len(company_titles) > 0 else 0} postings)
            - **Experience Level**: Typically requires {company_jobs['exp_min'].median()}-{company_jobs['exp_max'].median()} years of experience
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error analyzing company data: {e}")
        st.info("Please check your data files and try refreshing the page.")
        
# Updated Raw Data Page function
def raw_data_page(all_jobs, filtered_jobs, analyst_jobs):
    """
    Display the Raw Data page with improved styling and interactivity
    """
    st.markdown('<div class="section-header">Data</div>', unsafe_allow_html=True)
    
    # Create tabs for different datasets
    tab1, tab2, tab3 = st.tabs(["All Jobs", "Data-Related Jobs", "Analyst Jobs"])
    
    with tab1:
        if all_jobs is not None:
            st.markdown('<div class="subsection-header">All Jobs Dataset</div>', unsafe_allow_html=True)
            
            # Dataset statistics with modern metric cards
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="value">{all_jobs['Company'].nunique()}</div>
                    <div class="label">Unique Companies</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="value">{all_jobs['Job Title'].nunique()}</div>
                    <div class="label">Unique Job Titles</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Show sample data
            st.markdown('<div class="subsection-header">Sample Data</div>', unsafe_allow_html=True)
            st.dataframe(all_jobs, use_container_width=True)
            
            # Allow downloading the data with a more prominent button
            csv = all_jobs.to_csv(index=False)
            st.download_button(
                label="📥 Download All Jobs Data as CSV",
                data=csv,
                file_name="all_jobs.csv",
                mime="text/csv"
            )
        else:
            st.info("All jobs dataset is not available.")
    
    with tab2:
        st.markdown('<div class="subsection-header">Data-Related Jobs Dataset</div>', unsafe_allow_html=True)
        
        # Dataset statistics with modern metric cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{filtered_jobs['Company'].nunique()}</div>
                <div class="label">Unique Companies</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{filtered_jobs['Job Title'].nunique()}</div>
                <div class="label">Unique Job Titles</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{filtered_jobs['exp_min'].mean():.1f}</div>
                <div class="label">Avg Experience Req (Years)</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Data filters
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="subsection-header">Filter Data</div>', unsafe_allow_html=True)
        
        # Experience filter
        exp_min = int(filtered_jobs['exp_min'].min())
        exp_max = int(filtered_jobs['exp_max'].max() + 1)
        exp_range = st.slider(
            "Experience Required (Years)",
            min_value=exp_min,
            max_value=exp_max,
            value=(exp_min, exp_max),
            step=1
        )
        
        # Location filter
        locations = ['All'] + filtered_jobs['Location'].value_counts().nlargest(10).index.tolist()
        selected_location = st.selectbox("Location", options=locations)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Apply filters
        filtered_data = filtered_jobs.copy()
        
        # Experience filter
        filtered_data = filtered_data[
            (filtered_data['exp_min'] >= exp_range[0]) & 
            (filtered_data['exp_min'] <= exp_range[1])
        ]
        
        # Location filter
        if selected_location != 'All':
            filtered_data = filtered_data[filtered_data['Location'] == selected_location]
        
        # Show filtered data
        st.markdown(f'<div class="subsection-header">Filtered Data ({len(filtered_data)} records)</div>', unsafe_allow_html=True)
        
        # Select columns to display
        display_cols = st.multiselect(
            "Select columns to display",
            options=filtered_data.columns.tolist(),
            default=['Job Title', 'Company', 'Location', 'Min_Salary', 'Max_Salary', 'exp_min', 'exp_max', 'Date']
        )
        
        if display_cols:
            st.dataframe(filtered_data[display_cols], use_container_width=True)
        else:
            st.dataframe(filtered_data, use_container_width=True)
        
        # Allow downloading the filtered data
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_jobs.csv",
            mime="text/csv"
        )
    
    with tab3:
        if analyst_jobs is not None:
            st.markdown('<div class="subsection-header">Analyst Jobs Dataset</div>', unsafe_allow_html=True)
            
            # Dataset statistics with modern metric cards
            col1, col2, col3 = st.columns(3)
            
                   # Dataset statistics with modern metric cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{analyst_jobs['Company'].nunique()}</div>
                <div class="label">Unique Companies</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{analyst_jobs['Job Title'].nunique()}</div>
                <div class="label">Unique Job Titles</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{analyst_jobs['exp_min'].mean():.1f}</div>
                <div class="label">Avg Experience Req (Years)</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Data filters
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
            
            # Show sample data
        st.markdown('<div class="subsection-header">Sample Data </div>', unsafe_allow_html=True)
            
            # Format skills columns for display
        display_data = analyst_jobs.copy()
           
            
        st.dataframe(display_data, use_container_width=True)
            
            # Allow downloading the data
            # Convert skills lists to strings for CSV
        analyst_jobs_csv = analyst_jobs.copy()

            
        csv = analyst_jobs_csv.to_csv(index=False)
        st.download_button(
                label="📥 Download Analyst Jobs Data as CSV",
                data=csv,
                file_name="analyst_jobs.csv",
                mime="text/csv"
            )

            
# Main app function - final version
def main():
    """
    Main application function with navigation handling
    """
    # Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state.page = "Overview"
    
   # Sidebar navigation with modern styling
    with st.sidebar:
        st.title("Job Market Analysis")
        
        # Define page icons and labels
        pages = {
            "Overview": {"label": "Overview"},
            "Job Distribution": {"label": "Job Distribution"},
            "Salary Analysis": {"label": "Salary Analysis"},
            "Skills Analysis": {"label": "Skills Analysis"},
            "Company Analysis": {"label": "Company Analysis"},
            "Data": {"label": "Data"}
        }
        
        st.markdown("---")
        st.markdown('<div style="padding: 10px 0;">', unsafe_allow_html=True)
        
        # CSS for custom button styling
        st.markdown("""
        <style>
            div[data-testid="stButton"] button {
                background-color: #00dbd8; 
                color: white;
                font-weight: bold;
                text-align:left;
                border: none;
                transition: all 0.3s;
            }
            div[data-testid="stButton"] button[kind="secondary"] {
                background-color: #ebefef;
                text-align:left;
                color: #262730;
            }
            div[data-testid="stButton"] button:hover {
                background-color: #00dbd8;
                text-align:left;
                color: white;
            }
            div[data-testid="stButton"] button[kind="secondary"]:hover {
                background-color: #dff8f8;
                text-align:left;
                color: #262730;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Create modern navigation menu
        for page_name, page_info in pages.items():
            # Check if this is the active page
            is_active = st.session_state.page == page_name
            active_class = "active" if is_active else ""
            
            # Create a button for each page with styling based on active state
            if st.button(
                f"{page_info['label']}",
                key=f"nav_{page_name.lower().replace(' ', '_')}",
                help=f"",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.page = page_name
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Load data
    try:
        all_jobs_path = DATA_DIR / "processed_data.csv"
        filtered_jobs_path = DATA_DIR / "filtered_data.csv"
        analyst_jobs_path = DATA_DIR / "analyst_jobs.csv"
        
        all_jobs = load_data(all_jobs_path)
        filtered_jobs = load_data(filtered_jobs_path)
        analyst_jobs = load_data(analyst_jobs_path)
        
        if analyst_jobs is not None:
            analyst_jobs = convert_string_to_list(analyst_jobs, ['Soft Skills', 'Hard Skills', 'Domains'])
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please check that the data files exist in the correct location.")
        return
    
    # Check if data is loaded successfully
    if filtered_jobs is None:
        st.error("Could not load the filtered jobs data. Please check the data files.")
        return
    
    # Display the appropriate page based on session state
    if st.session_state.page == "Overview":
        overview_page(filtered_jobs, all_jobs, analyst_jobs)
    elif st.session_state.page == "Job Distribution":
        # Add main header for consistency across pages
        st.markdown('<div class="main-header">Vietnamese Data Job Market Analysis</div>', unsafe_allow_html=True)
        job_distribution_page(filtered_jobs)
    elif st.session_state.page == "Salary Analysis":
        st.markdown('<div class="main-header">Vietnamese Data Job Market Analysis</div>', unsafe_allow_html=True)
        salary_analysis(filtered_jobs)
    elif st.session_state.page == "Skills Analysis":
        st.markdown('<div class="main-header">Vietnamese Data Job Market Analysis</div>', unsafe_allow_html=True)
        skills_analysis_page(analyst_jobs)
    elif st.session_state.page == "Company Analysis":
        st.markdown('<div class="main-header">Vietnamese Data Job Market Analysis</div>', unsafe_allow_html=True)
        company_analysis_page(filtered_jobs)
    elif st.session_state.page == "Data":
        st.markdown('<div class="main-header">Vietnamese Data Job Market Analysis</div>', unsafe_allow_html=True)
        raw_data_page(all_jobs, filtered_jobs, analyst_jobs)

# Run the app
if __name__ == "__main__":
    main()