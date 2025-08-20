"""
Real Boston Housing Data Processor
Use actual Boston metro data from Zillow instead of fake neighborhood data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class RealBostonProcessor:
    """Process REAL Boston housing data from Zillow"""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.boston_metro_code = 394404  # Boston, MA metro area
    
    def load_data(self) -> pd.DataFrame:
        """Load Zillow housing data"""
        try:
            df = pd.read_csv(self.data_path)
            logger.info(f"Loaded Zillow data: {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"Error loading Zillow data: {e}")
            return pd.DataFrame()
    
    def filter_boston_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter for Boston metro area only"""
        boston_data = df[df['RegionID'] == self.boston_metro_code]
        logger.info(f"Found Boston data: {len(boston_data)} rows")
        return boston_data
    
    def extract_monthly_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract monthly rental prices from wide format"""
        # Get date columns (all columns that look like dates)
        date_columns = [col for col in df.columns if col.startswith('20') and '-' in col]
        
        if not date_columns:
            logger.warning("No date columns found in Zillow data")
            return pd.DataFrame()
        
        # Melt the data to long format
        melted = df.melt(
            id_vars=['RegionID', 'SizeRank', 'RegionName', 'RegionType', 'StateName'],
            value_vars=date_columns,
            var_name='date',
            value_name='rental_price'
        )
        
        # Convert date strings to datetime
        melted['date'] = pd.to_datetime(melted['date'])
        melted['month'] = melted['date'].dt.to_period('M')
        
        # Clean up rental prices
        melted['rental_price'] = pd.to_numeric(melted['rental_price'], errors='coerce')
        
        # Remove rows with missing prices
        melted = melted.dropna(subset=['rental_price'])
        
        logger.info(f"Extracted monthly prices: {len(melted)} records")
        return melted
    
    def calculate_housing_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive housing metrics for Boston"""
        if df.empty:
            return pd.DataFrame()
        
        # Create metrics dataframe
        metrics = df.copy()
        
        # Rename columns for clarity
        metrics = metrics.rename(columns={
            'rental_price': 'median_rent',
            'RegionName': 'metro_area'
        })
        
        # Calculate additional metrics
        metrics['avg_rent'] = metrics['median_rent']  # Same as median for single metro area
        metrics['rent_std'] = 0  # No variation within single metro area
        
        # Calculate affordability (assuming student budget of $2000/month)
        student_budget = 2000
        metrics['affordability_ratio'] = metrics['median_rent'] / student_budget
        metrics['is_affordable'] = metrics['affordability_ratio'] <= 1.0
        
        # Calculate year-over-year change
        metrics['month'] = metrics['month'].astype(str)
        metrics['year'] = pd.to_datetime(metrics['month'] + '-01').dt.year
        
        # Sort by date for proper YoY calculation
        metrics = metrics.sort_values('date')
        
        # YoY change calculation
        metrics['prev_year_rent'] = metrics['median_rent'].shift(12)
        metrics['yoy_change'] = (metrics['median_rent'] - metrics['prev_year_rent']) / metrics['prev_year_rent'] * 100
        
        # Add neighborhood column for compatibility (using metro area name)
        metrics['neighborhood'] = 'Boston Metro Area'
        
        # Select and reorder columns
        final_columns = [
            'neighborhood', 'month', 'avg_rent', 'median_rent', 'rent_std',
            'affordability_ratio', 'is_affordable', 'year', 'prev_year_rent', 'yoy_change'
        ]
        
        result = metrics[final_columns]
        
        logger.info(f"Calculated housing metrics: {len(result)} records")
        return result
    
    def process_all(self) -> pd.DataFrame:
        """Process all Boston housing data"""
        try:
            print("Processing REAL Boston housing data from Zillow...")
            
            # Load data
            df = self.load_data()
            if df.empty:
                return pd.DataFrame()
            
            # Filter Boston data
            boston_df = self.filter_boston_data(df)
            if boston_df.empty:
                print("No Boston data found!")
                return pd.DataFrame()
            
            # Extract monthly prices
            monthly_df = self.extract_monthly_prices(boston_df)
            if monthly_df.empty:
                print("No monthly price data found!")
                return pd.DataFrame()
            
            # Calculate metrics
            metrics_df = self.calculate_housing_metrics(monthly_df)
            
            print(f"Processed {len(metrics_df)} housing records")
            print("\nSample data:")
            print(metrics_df.head().to_string())
            
            # Save processed data
            output_path = Path("data/processed/boston_housing_data.csv")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            metrics_df.to_csv(output_path, index=False)
            print(f"\nSaved to: {output_path}")
            
            return metrics_df
            
        except Exception as e:
            print(f"Error processing housing data: {e}")
            return pd.DataFrame()

def main():
    """Test real Boston data processing"""
    processor = RealBostonProcessor(Path("data/raw/Metro_zori_uc_sfrcondomfr_sm_month.csv"))
    result = processor.process_all()
    
    if not result.empty:
        print(f"\n✅ Successfully processed {len(result)} REAL Boston housing records")
        print(f"📊 Data range: {result['month'].min()} to {result['month'].max()}")
        print(f"💰 Current median rent: ${result[result['month'] == result['month'].max()]['median_rent'].iloc[0]:.0f}")
        print(f"📈 YoY change: {result[result['month'] == result['month'].max()]['yoy_change'].iloc[0]:.1f}%")
    else:
        print("❌ No data processed")

if __name__ == "__main__":
    main()
