"""
Enhanced Boston Resource Optimizer
Real-time transit + Comprehensive housing + Interactive maps + Matplotlib graphs
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib.patches import Rectangle
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.mbta_api import MBTAAPI
from src.real_boston_processor import RealBostonProcessor

# Page config
st.set_page_config(
    page_title="Boston Resource Optimizer",
    page_icon="🏙️",
    layout="wide"
)

# Set matplotlib style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .student-tip {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .student-tip h4 {
        color: white;
        font-size: 1.3rem;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: bold;
    }
    .student-tip ul {
        margin: 0;
        padding-left: 1.5rem;
    }
    .student-tip li {
        margin-bottom: 0.5rem;
        line-height: 1.6;
    }
    .student-tip strong {
        color: #ffd700;
        font-weight: bold;
    }
    .tips-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .tips-header h2 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    .tips-header p {
        font-size: 1.2rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

def load_housing_data():
    """Load Boston housing data"""
    try:
        housing_path = Path("data/processed/boston_housing_data.csv")
        if housing_path.exists():
            return pd.read_csv(housing_path)
        else:
            processor = RealBostonProcessor(Path("data/raw/Metro_zori_uc_sfrcondomfr_sm_month.csv"))
            return processor.process_all()
    except Exception as e:
        st.error(f"Error loading housing data: {e}")
        return pd.DataFrame()

def create_housing_analysis_charts(data):
    """Create comprehensive housing analysis with matplotlib"""
    if data.empty:
        return None
    
    # Convert month to datetime
    data['date'] = pd.to_datetime(data['month'].astype(str) + '-01')
    
    # Create subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Rent Trends Over Time
    ax1.plot(data['date'], data['median_rent'], linewidth=3, marker='o', markersize=4, color='#1f77b4')
    ax1.set_title('Boston Metro Rent Trends (2015-2025)', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Median Rent ($)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_locator(mdates.YearLocator(2))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # Add trend line
    z = np.polyfit(range(len(data)), data['median_rent'], 1)
    p = np.poly1d(z)
    ax1.plot(data['date'], p(range(len(data))), "r--", alpha=0.8, linewidth=2, label='Trend')
    ax1.legend()
    
    # 2. YoY Change Analysis
    yoy_data = data.groupby('year')['yoy_change'].mean()
    colors = ['red' if x < 0 else 'green' for x in yoy_data.values]
    bars = ax2.bar(yoy_data.index, yoy_data.values, color=colors, alpha=0.7)
    ax2.set_title('Year-over-Year Rent Change', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('YoY Change (%)', fontsize=12)
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax2.grid(True, alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(yoy_data.values):
        if not np.isnan(v):
            ax2.text(yoy_data.index[i], v + (0.5 if v > 0 else -0.5), 
                    f'{v:.1f}%', ha='center', va='bottom' if v > 0 else 'top', fontweight='bold')
    
    # 3. Monthly Rent Patterns
    monthly_breakdown = data.groupby(data['date'].dt.month)['median_rent'].mean()
    ax3.bar(monthly_breakdown.index, monthly_breakdown.values, color='lightgreen', alpha=0.7)
    ax3.set_title('Monthly Rent Patterns (All Years)', fontsize=16, fontweight='bold')
    ax3.set_xlabel('Month', fontsize=12)
    ax3.set_ylabel('Average Rent ($)', fontsize=12)
    ax3.set_xticks(range(1, 13))
    ax3.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax3.grid(True, alpha=0.3)
    
    # 4. Affordability Analysis
    student_budget = 2000
    data['budget_gap'] = data['median_rent'] - student_budget
    ax4.plot(data['date'], data['budget_gap'], linewidth=2, color='orange', marker='s')
    ax4.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Student Budget ($2000)')
    ax4.fill_between(data['date'], data['budget_gap'], 0, 
                     where=(data['budget_gap'] > 0), color='red', alpha=0.3, label='Over Budget')
    ax4.fill_between(data['date'], data['budget_gap'], 0, 
                     where=(data['budget_gap'] < 0), color='green', alpha=0.3, label='Under Budget')
    ax4.set_title('Student Budget Gap Analysis', fontsize=16, fontweight='bold')
    ax4.set_xlabel('Year', fontsize=12)
    ax4.set_ylabel('Budget Gap ($)', fontsize=12)
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    return fig

def create_mbta_analysis_charts(routes, vehicles, alerts):
    """Create comprehensive MBTA analysis charts"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Route Distribution by Type
    if not routes.empty:
        route_types = routes['route_type'].value_counts()
        colors = plt.cm.Set3(np.linspace(0, 1, len(route_types)))
        wedges, texts, autotexts = ax1.pie(route_types.values, labels=route_types.index, 
                                          autopct='%1.1f%%', startangle=90, colors=colors)
        ax1.set_title('MBTA Routes by Type', fontsize=16, fontweight='bold')
    
    # 2. Vehicle Status Distribution
    if not vehicles.empty:
        status_counts = vehicles['current_status'].value_counts()
        colors = plt.cm.Set3(np.linspace(0, 1, len(status_counts)))
        bars = ax2.bar(range(len(status_counts)), status_counts.values, color=colors)
        ax2.set_title('Vehicle Status Distribution', fontsize=16, fontweight='bold')
        ax2.set_xlabel('Status', fontsize=12)
        ax2.set_ylabel('Number of Vehicles', fontsize=12)
        ax2.set_xticks(range(len(status_counts)))
        ax2.set_xticklabels(status_counts.index, rotation=45)
        
        # Add value labels
        for i, v in enumerate(status_counts.values):
            ax2.text(i, v + 0.1, str(v), ha='center', va='bottom', fontweight='bold')
    
    # 3. Alert Severity Analysis
    if not alerts.empty:
        severity_counts = alerts['severity'].value_counts()
        colors = ['red', 'orange', 'yellow'][:len(severity_counts)]
        bars = ax3.bar(range(len(severity_counts)), severity_counts.values, color=colors, alpha=0.7)
        ax3.set_title('Service Alert Severity', fontsize=16, fontweight='bold')
        ax3.set_xlabel('Severity Level', fontsize=12)
        ax3.set_ylabel('Number of Alerts', fontsize=12)
        ax3.set_xticks(range(len(severity_counts)))
        ax3.set_xticklabels(severity_counts.index)
        
        # Add value labels
        for i, v in enumerate(severity_counts.values):
            ax3.text(i, v + 0.1, str(v), ha='center', va='bottom', fontweight='bold')
    
    # 4. System Health Overview
    total_routes = len(routes) if not routes.empty else 0
    active_vehicles = len(vehicles) if not vehicles.empty else 0
    active_alerts = len(alerts) if not alerts.empty else 0
    
    metrics = ['Routes', 'Active Vehicles', 'Active Alerts']
    values = [total_routes, active_vehicles, active_alerts]
    colors = ['lightblue', 'lightgreen', 'lightcoral']
    
    bars = ax4.bar(metrics, values, color=colors, alpha=0.7)
    ax4.set_title('MBTA System Overview', fontsize=16, fontweight='bold')
    ax4.set_ylabel('Count', fontsize=12)
    
    # Add value labels on bars
    for i, v in enumerate(values):
        ax4.text(i, v + 0.1, str(v), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    return fig

def create_comprehensive_boston_map():
    """Create comprehensive Boston map with universities, neighborhoods, and MBTA"""
    m = folium.Map(location=[42.3601, -71.0589], zoom_start=11, tiles='OpenStreetMap')
    
    # Major Universities with detailed info
    universities = {
        'Boston University': {
            'coords': [42.3505, -71.1054],
            'students': '35,000+',
            'avg_rent_nearby': '$2,800',
            'mbta_lines': 'Green Line B, C, D',
            'pros': 'Student-friendly, nightlife, near Fenway',
            'cons': 'Can be expensive, noisy'
        },
        'Northeastern University': {
            'coords': [42.3398, -71.0892],
            'students': '28,000+',
            'avg_rent_nearby': '$2,900',
            'mbta_lines': 'Green Line E, Orange Line',
            'pros': 'Co-op programs, near museums',
            'cons': 'Expensive area, limited parking'
        },
        'MIT': {
            'coords': [42.3601, -71.0942],
            'students': '11,000+',
            'avg_rent_nearby': '$3,200',
            'mbta_lines': 'Red Line, Green Line',
            'pros': 'Tech hub, innovation center',
            'cons': 'Very expensive, competitive housing'
        },
        'Harvard University': {
            'coords': [42.3744, -71.1169],
            'students': '31,000+',
            'avg_rent_nearby': '$3,100',
            'mbta_lines': 'Red Line',
            'pros': 'Prestigious, historic area',
            'cons': 'Expensive, limited student housing'
        },
        'Boston College': {
            'coords': [42.3354, -71.1685],
            'students': '14,000+',
            'avg_rent_nearby': '$2,600',
            'mbta_lines': 'Green Line B, C',
            'pros': 'Beautiful campus, quieter area',
            'cons': 'Far from downtown, limited nightlife'
        },
        'UMass Boston': {
            'coords': [42.3149, -71.0356],
            'students': '16,000+',
            'avg_rent_nearby': '$2,200',
            'mbta_lines': 'Red Line',
            'pros': 'Affordable area, waterfront',
            'cons': 'Limited amenities, industrial area'
        },
        'Emerson College': {
            'coords': [42.3598, -71.0641],
            'students': '4,000+',
            'avg_rent_nearby': '$3,300',
            'mbta_lines': 'Green Line, Red Line',
            'pros': 'Downtown location, arts focus',
            'cons': 'Very expensive, touristy area'
        },
        'Suffolk University': {
            'coords': [42.3584, -71.0596],
            'students': '7,000+',
            'avg_rent_nearby': '$3,200',
            'mbta_lines': 'Green Line, Red Line',
            'pros': 'Downtown, business focus',
            'cons': 'Expensive, limited campus feel'
        }
    }
    
    # Add universities with detailed popups
    for uni, info in universities.items():
        popup_content = f"""
        <div style='width: 300px;'>
            <h4 style='color: #1f77b4;'>{uni}</h4>
            <p><strong>Students:</strong> {info['students']}</p>
            <p><strong>Avg Rent Nearby:</strong> {info['avg_rent_nearby']}/month</p>
            <p><strong>MBTA Lines:</strong> {info['mbta_lines']}</p>
            <p><strong>Pros:</strong> {info['pros']}</p>
            <p><strong>Cons:</strong> {info['cons']}</p>
        </div>
        """
        
        folium.Marker(
            info['coords'],
            popup=folium.Popup(popup_content, max_width=350),
            icon=folium.Icon(color='blue', icon='graduation-cap', prefix='fa'),
            tooltip=uni
        ).add_to(m)
    
    # Student-friendly neighborhoods
    neighborhoods = {
        'Allston': {'coords': [42.3528, -71.1342], 'avg_rent': 2800, 'student_friendly': True},
        'Dorchester': {'coords': [42.3150, -71.0275], 'avg_rent': 2200, 'student_friendly': True},
        'East Boston': {'coords': [42.3681, -70.9956], 'avg_rent': 2400, 'student_friendly': True},
        'Hyde Park': {'coords': [42.2544, -71.1253], 'avg_rent': 2000, 'student_friendly': True},
        'Jamaica Plain': {'coords': [42.3097, -71.1061], 'avg_rent': 2600, 'student_friendly': True},
        'Roxbury': {'coords': [42.3118, -71.0851], 'avg_rent': 2200, 'student_friendly': True},
        'Mattapan': {'coords': [42.2676, -71.0944], 'avg_rent': 2100, 'student_friendly': True}
    }
    
    # Add neighborhoods
    for name, info in neighborhoods.items():
        color = 'green' if info['student_friendly'] else 'red'
        size = 12 if info['student_friendly'] else 8
        
        popup_content = f"""
        <div style='width: 250px;'>
            <h4 style='color: {color};'>{name}</h4>
            <p><strong>Avg Rent:</strong> ${info['avg_rent']:,}/month</p>
            <p><strong>Student Friendly:</strong> {'✅ Yes' if info['student_friendly'] else '❌ No'}</p>
            <p><strong>Best for:</strong> Students on a budget</p>
        </div>
        """
        
        folium.CircleMarker(
            location=info['coords'],
            radius=size,
            popup=folium.Popup(popup_content, max_width=300),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            tooltip=f"{name} - ${info['avg_rent']:,}/month"
        ).add_to(m)
    
    # Major MBTA stations
    mbta_stations = {
        'Park Street': [42.3564, -71.0624],
        'Downtown Crossing': [42.3555, -71.0604],
        'Government Center': [42.3597, -71.0592],
        'Haymarket': [42.3638, -71.0584],
        'North Station': [42.3662, -71.0631],
        'South Station': [42.3519, -71.0552],
        'Back Bay': [42.3473, -71.0752],
        'Kenmore': [42.3489, -71.0953],
        'Harvard Square': [42.3734, -71.1189],
        'Central Square': [42.3654, -71.1036],
        'Kendall/MIT': [42.3625, -71.0862],
        'Charles/MGH': [42.3612, -71.0706]
    }
    
    for station, coords in mbta_stations.items():
        folium.Marker(
            coords,
            popup=f"<b>MBTA: {station}</b><br>Major transit hub",
            icon=folium.Icon(color='orange', icon='train', prefix='fa'),
            tooltip=f"MBTA: {station}"
        ).add_to(m)
    
    return m

def main():
    st.markdown('<h1 class="main-header">🏙️ Boston Resource Optimizer</h1>', unsafe_allow_html=True)
    st.markdown("### **Enhanced Dashboard: Real-time Transit • Comprehensive Housing • Interactive Maps**")
    
    # Load data
    with st.spinner("Loading real Boston data..."):
        housing_data = load_housing_data()
        mbta = MBTAAPI()
    
    # Top-level metrics
    st.markdown("---")
    st.subheader("📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not housing_data.empty:
            latest_rent = housing_data[housing_data['month'] == housing_data['month'].max()]['median_rent'].iloc[0]
            st.metric("🏠 Current Median Rent", f"${latest_rent:.0f}", "Boston Metro")
    
    with col2:
        if not housing_data.empty:
            latest_data = housing_data[housing_data['month'] == housing_data['month'].max()].iloc[0]
            yoy_change = latest_data['yoy_change']
            if pd.notna(yoy_change):
                st.metric("📈 YoY Change", f"{yoy_change:.1f}%", "Rent Growth")
            else:
                st.metric("📈 YoY Change", "N/A", "Rent Growth")
    
    with col3:
        routes = mbta.get_routes()
        st.metric("🚇 MBTA Routes", len(routes) if not routes.empty else 0, "Active")
    
    with col4:
        alerts = mbta.get_service_alerts()
        st.metric("🚨 Service Alerts", len(alerts) if not alerts.empty else 0, "Active")
    
    st.markdown("---")
    
    # Housing Analysis Section
    st.header("🏠 Comprehensive Housing Analysis")
    
    if not housing_data.empty:
        # Create comprehensive housing charts
        housing_fig = create_housing_analysis_charts(housing_data)
        if housing_fig:
            st.pyplot(housing_fig)
        
        # Additional insights
        col1, col2, col3 = st.columns(3)
        with col1:
            latest_data = housing_data[housing_data['month'] == housing_data['month'].max()].iloc[0]
            st.metric("📊 Rent Range", f"${housing_data['median_rent'].min():.0f} - ${housing_data['median_rent'].max():.0f}", "Min-Max")
        
        with col2:
            st.metric("📅 Data Points", len(housing_data), "Records")
        
        with col3:
            student_budget = 2000
            latest_rent = housing_data[housing_data['month'] == housing_data['month'].max()]['median_rent'].iloc[0]
            budget_gap = latest_rent - student_budget
            st.metric("💰 Student Budget Gap", f"${budget_gap:.0f}", f"Over ${student_budget} budget")
        
        # Show latest data
        st.subheader("📋 Latest Housing Report")
        latest_month = housing_data['month'].max()
        latest_info = housing_data[housing_data['month'] == latest_month].iloc[0]
        
        yoy_change = latest_info['yoy_change']
        yoy_text = f"{yoy_change:.1f}%" if pd.notna(yoy_change) else "N/A"
        
        st.info(f"""
        **{latest_month} Housing Report:**
        - **Median Rent:** ${latest_info['median_rent']:.0f}/month
        - **Student Budget Gap:** ${latest_info['median_rent'] - 2000:.0f}/month over $2000 budget
        - **YoY Change:** {yoy_text} from previous year
        - **Affordability:** {'❌ Not Affordable' if latest_info['median_rent'] > 2000 else '✅ Affordable'} for students
        """)
        
        # Show data table
        st.subheader("📊 Recent Housing Data")
        recent_data = housing_data.tail(15)[['month', 'median_rent', 'yoy_change']].copy()
        recent_data['yoy_change'] = recent_data['yoy_change'].fillna('N/A')
        st.dataframe(recent_data, use_container_width=True)
    else:
        st.error("Housing data not available")
    
    st.markdown("---")
    
    # MBTA Real-Time Analysis Section
    st.header("🚇 MBTA Real-Time System Analysis")
    
    # Get comprehensive MBTA data
    with st.spinner("Loading real-time MBTA data..."):
        routes = mbta.get_routes()
        
    if not routes.empty:
        # Route selector for detailed analysis
        route_names = routes['route_name'].tolist()
        selected_route = st.selectbox("Select MBTA Route for Detailed Analysis", route_names)
        
        if selected_route:
            route_id = routes[routes['route_name'] == selected_route]['route_id'].iloc[0]
            
            # Get detailed data
            vehicles = mbta.get_vehicles(route_id)
            alerts = mbta.get_service_alerts(route_id)
            
            # Create MBTA analysis charts
            mbta_fig = create_mbta_analysis_charts(routes, vehicles, alerts)
            if mbta_fig:
                st.pyplot(mbta_fig)
            
            # Real-time alerts
            if not alerts.empty:
                st.subheader("🚨 Active Service Alerts")
                for _, alert in alerts.head(5).iterrows():
                    header = alert['header'] or "No header"
                    description = alert['description'] or "No description available"
                    severity = alert.get('severity', 'Unknown')
                    
                    if severity == 3:
                        st.error(f"**{header}**\n{description[:200]}...")
                    elif severity == 2:
                        st.warning(f"**{header}**\n{description[:200]}...")
                    else:
                        st.info(f"**{header}**\n{description[:200]}...")
            else:
                st.success("✅ No active service alerts for this route")
            
            # Route details
            st.subheader(f"📋 {selected_route} Route Details")
            route_info = routes[routes['route_name'] == selected_route].iloc[0]
            st.info(f"""
            **Route Information:**
            - **Type:** {route_info['route_type']}
            - **Active Vehicles:** {len(vehicles)} vehicles
            - **Service Alerts:** {len(alerts)} active alerts
            - **Route ID:** {route_info['route_id']}
            """)
    else:
        st.error("Could not load MBTA data")
    
    st.markdown("---")
    
    # Interactive Map Section
    st.header("🗺️ Interactive Boston Map - University & Housing Guide")
    st.markdown("**Click on universities, neighborhoods, and MBTA stations for detailed information**")
    
    # Create comprehensive map
    boston_map = create_comprehensive_boston_map()
    
    # Display map
    map_data = st_folium(boston_map, width=1200, height=600)
    
    # Show clicked location info
    if map_data['last_clicked']:
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lng = map_data['last_clicked']['lng']
        st.info(f"📍 **Selected Location:** {clicked_lat:.4f}, {clicked_lng:.4f}")
    
    st.markdown("---")
    
    # Student Resources Section
    st.markdown("""
    <div class="tips-header">
        <h2>🎓 Student Resources & Tips</h2>
        <p>Everything you need to know about housing, transit, and budgeting in Boston</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="student-tip">
            <h4>💰 Smart Budget Planning</h4>
            <ul>
                <li><strong>Target Rent:</strong> $2000/month or less</li>
                <li><strong>Utilities:</strong> $200-300/month (heat, electricity, internet)</li>
                <li><strong>Transportation:</strong> MBTA pass $90/month (unlimited rides)</li>
                <li><strong>Food & Groceries:</strong> $400-600/month</li>
                <li><strong>Emergency Fund:</strong> Save $500-1000 for unexpected costs</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="student-tip">
            <h4>🏘️ Top Student Neighborhoods</h4>
            <ul>
                <li><strong>Allston:</strong> Student hub near BU, nightlife, $2800 avg</li>
                <li><strong>Dorchester:</strong> Most affordable, diverse community, $2200 avg</li>
                <li><strong>East Boston:</strong> Airport access, waterfront, $2400 avg</li>
                <li><strong>Hyde Park:</strong> Quiet, family-friendly, $2000 avg</li>
                <li><strong>Jamaica Plain:</strong> Hip, artsy, parks, $2600 avg</li>
                <li><strong>Roxbury:</strong> Historic, affordable, $2200 avg</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="student-tip">
            <h4>🚇 MBTA Transit Guide</h4>
            <ul>
                <li><strong>Monthly Pass:</strong> $90 for unlimited rides (best value)</li>
                <li><strong>Student Discount:</strong> Available through universities</li>
                <li><strong>Best Lines:</strong> Red Line (Harvard, MIT), Green Line (BU, BC)</li>
                <li><strong>Late Night:</strong> Limited service after midnight</li>
                <li><strong>Real-time Updates:</strong> Use MBTA app for live tracking</li>
                <li><strong>Bike Access:</strong> Most trains allow bikes during off-peak</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="student-tip">
            <h4>📅 Housing Timeline & Tips</h4>
            <ul>
                <li><strong>Fall Semester:</strong> Start looking in March-April (peak season)</li>
                <li><strong>Spring Semester:</strong> Start looking in October-November</li>
                <li><strong>Summer:</strong> Sublets available, cheaper rates</li>
                <li><strong>Roommates:</strong> Can reduce costs by 30-50%</li>
                <li><strong>Security Deposit:</strong> Usually 1 month rent + first month</li>
                <li><strong>Application Fee:</strong> $25-50 per application</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Additional Tips Section
    st.markdown("---")
    st.subheader("💡 Pro Tips for Boston Students")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **🎯 Quick Start Checklist:**
        - Set up MBTA account with student discount
        - Join university housing Facebook groups
        - Download MBTA and Boston apps
        - Research neighborhoods on the map above
        - Start saving for security deposit
        """)
    
    with col2:
        st.success("""
        **🚨 Red Flags to Avoid:**
        - Rent significantly below market rate
        - Landlord won't show apartment in person
        - No written lease agreement
        - Cash-only payments
        - No background check required
        """)
    
    with col3:
        st.warning("""
        **📱 Essential Apps:**
        - MBTA (transit)
        - Boston Globe (local news)
        - Zillow/RentHop (housing)
        - Uber/Lyft (backup transport)
        - Weather apps (Boston weather is unpredictable!)
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Boston Resource Optimizer</strong> - Enhanced Dashboard</p>
        <p>Real-time MBTA data • Comprehensive housing analysis • Interactive maps</p>
        <p>Built for Boston students and residents</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
