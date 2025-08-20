# Boston Resource Optimizer

A comprehensive dashboard for Boston students to find housing and transit information with real-time data.

## 🚀 Live Demo

**Deploy this app on Streamlit Cloud:**
1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Deploy!

## Features

- **🏠 Real Housing Data**: Boston metro rental prices from Zillow (2015-2025)
- **🚇 Live MBTA Data**: Real-time transit information using MBTA V3 API
- **🗺️ Interactive Maps**: Boston universities, neighborhoods, and MBTA stations
- **📊 Beautiful Charts**: Matplotlib visualizations with comprehensive analysis
- **🎓 Student Resources**: Budget planning and housing tips

## Quick Start

### Local Development

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd COR
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard:**
   ```bash
   streamlit run src/enhanced_dashboard.py
   ```

4. **Open your browser** to `http://localhost:8501`

### Streamlit Cloud Deployment

1. **Fork this repository** to your GitHub account
2. **Go to [share.streamlit.io](https://share.streamlit.io)**
3. **Sign in** with your GitHub account
4. **Click "New app"**
5. **Select your forked repository**
6. **Set the main file path:** `src/enhanced_dashboard.py`
7. **Click "Deploy"**

## Data Sources

- **Housing**: Zillow rental data for Boston metro area (2015-2025)
- **Transit**: MBTA V3 API (real-time data)
- **Map**: OpenStreetMap with university and neighborhood data

## Project Structure

```
COR/
├── src/
│   ├── enhanced_dashboard.py      # 🎯 MAIN DASHBOARD
│   ├── real_boston_processor.py   # Housing data processor
│   ├── mbta_api.py               # MBTA API client
│   └── __init__.py
├── data/
│   ├── raw/
│   │   └── Metro_zori_uc_sfrcondomfr_sm_month.csv  # Zillow data
│   └── processed/
│       └── boston_housing_data.csv                 # Processed housing data
├── requirements.txt
└── README.md
```

## What You'll See

### 📊 Key Metrics
- Current median rent in Boston metro area
- Year-over-year rent changes
- Live MBTA route count
- Active service alerts

### 🏠 Housing Analysis
- **4 Comprehensive Charts:**
  - Rent trends over time (2015-2025)
  - Year-over-year change analysis
  - Monthly rent patterns
  - Student budget gap analysis
- Recent housing data table
- Student affordability insights

### 🚇 MBTA Real-Time Data
- **4 MBTA Analysis Charts:**
  - Route distribution by type
  - Vehicle status distribution
  - Service alert severity
  - System health overview
- Route selector for detailed analysis
- Real-time service alerts
- Vehicle tracking

### 🗺️ Interactive Map
- **8 Major Universities** with detailed info:
  - Boston University, Northeastern, MIT, Harvard
  - Boston College, UMass Boston, Emerson, Suffolk
- **7 Student-friendly neighborhoods** with rent info
- **12 Major MBTA stations** with transit details
- Clickable popups with comprehensive information

### 🎓 Student Resources
- Budget planning tips
- Best student areas guide
- Transit tips and costs
- Housing timeline advice

## For Students

### 💰 Budget Planning
- **Target Budget:** $2000/month or less for rent
- **Utilities:** Add $200-300/month
- **Transportation:** MBTA pass ~$90/month
- **Food:** Budget $400-600/month

### 🏘️ Best Student Areas
- **Allston:** Near BU, lots of students, $2800 avg
- **Dorchester:** Affordable, diverse, $2200 avg
- **East Boston:** Airport access, $2400 avg
- **Hyde Park:** Most affordable, $2000 avg
- **Jamaica Plain:** Hip area, $2600 avg

### 🚇 Transit Tips
- **Monthly Pass:** $90 for unlimited rides
- **Student Discount:** Available through universities
- **Best Lines:** Red Line (Harvard, MIT), Green Line (BU, BC)
- **Real-time:** Use MBTA app for live updates

## API Keys

The MBTA API key is included in the code. For production use, consider using environment variables.

## Deployment Notes

- **Streamlit Cloud** automatically installs dependencies from `requirements.txt`
- **Data files** are included in the repository for immediate use
- **No external API keys** required for basic functionality
- **Real-time data** updates automatically when deployed

## Contributing

Feel free to contribute by:
- Adding more universities or neighborhoods
- Enhancing visualizations
- Improving the user interface
- Adding new data sources

## License

This project is open source and available under the MIT License.

---

**Built with ❤️ for Boston students and residents**


