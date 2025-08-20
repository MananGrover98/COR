"""
MBTA V3 API Integration
Real-time transit data for Boston students
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class MBTAAPI:
    """MBTA V3 API client for real-time transit data"""
    
    def __init__(self, api_key: str = "935d9450e0f942a884db998504d3ccf2"):
        self.api_key = api_key
        self.base_url = "https://api-v3.mbta.com"
        self.headers = {"x-api-key": api_key}
    
    def get_routes(self) -> pd.DataFrame:
        """Get all MBTA routes"""
        try:
            response = requests.get(f"{self.base_url}/routes", headers=self.headers)
            response.raise_for_status()
            data = response.json()["data"]
            
            routes = []
            for route in data:
                attrs = route["attributes"]
                routes.append({
                    "route_id": route["id"],
                    "route_name": attrs.get("long_name", ""),
                    "route_type": attrs.get("type", ""),
                    "route_color": attrs.get("color", ""),
                    "route_text_color": attrs.get("text_color", "")
                })
            
            return pd.DataFrame(routes)
        except Exception as e:
            logger.error(f"Error fetching routes: {e}")
            return pd.DataFrame()
    
    def get_stops(self, route_id: Optional[str] = None) -> pd.DataFrame:
        """Get stops for a specific route or all stops"""
        try:
            url = f"{self.base_url}/stops"
            if route_id:
                url += f"?filter[route]={route_id}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()["data"]
            
            stops = []
            for stop in data:
                attrs = stop["attributes"]
                stops.append({
                    "stop_id": stop["id"],
                    "stop_name": attrs.get("name", ""),
                    "stop_lat": attrs.get("latitude", 0),
                    "stop_lon": attrs.get("longitude", 0),
                    "wheelchair_boarding": attrs.get("wheelchair_boarding", 0),
                    "route_id": route_id
                })
            
            return pd.DataFrame(stops)
        except Exception as e:
            logger.error(f"Error fetching stops: {e}")
            return pd.DataFrame()
    
    def get_vehicles(self, route_id: Optional[str] = None) -> pd.DataFrame:
        """Get real-time vehicle locations"""
        try:
            url = f"{self.base_url}/vehicles"
            if route_id:
                url += f"?filter[route]={route_id}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()["data"]
            
            vehicles = []
            for vehicle in data:
                attrs = vehicle["attributes"]
                vehicles.append({
                    "vehicle_id": vehicle["id"],
                    "route_id": vehicle.get("relationships", {}).get("route", {}).get("data", {}).get("id", ""),
                    "latitude": attrs.get("latitude", 0),
                    "longitude": attrs.get("longitude", 0),
                    "bearing": attrs.get("bearing", 0),
                    "speed": attrs.get("speed", 0),
                    "current_status": attrs.get("current_status", ""),
                    "updated_at": attrs.get("updated_at", "")
                })
            
            return pd.DataFrame(vehicles)
        except Exception as e:
            logger.error(f"Error fetching vehicles: {e}")
            return pd.DataFrame()
    
    def get_predictions(self, stop_id: str) -> pd.DataFrame:
        """Get arrival predictions for a specific stop"""
        try:
            response = requests.get(f"{self.base_url}/predictions?filter[stop]={stop_id}", headers=self.headers)
            response.raise_for_status()
            data = response.json()["data"]
            
            predictions = []
            for pred in data:
                attrs = pred["attributes"]
                predictions.append({
                    "prediction_id": pred["id"],
                    "stop_id": stop_id,
                    "route_id": pred.get("relationships", {}).get("route", {}).get("data", {}).get("id", ""),
                    "arrival_time": attrs.get("arrival_time", ""),
                    "departure_time": attrs.get("departure_time", ""),
                    "direction_id": attrs.get("direction_id", 0),
                    "status": attrs.get("status", "")
                })
            
            return pd.DataFrame(predictions)
        except Exception as e:
            logger.error(f"Error fetching predictions: {e}")
            return pd.DataFrame()
    
    def get_service_alerts(self, route_id: Optional[str] = None) -> pd.DataFrame:
        """Get service alerts and delays"""
        try:
            url = f"{self.base_url}/alerts"
            if route_id:
                url += f"?filter[route]={route_id}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()["data"]
            
            alerts = []
            for alert in data:
                attrs = alert["attributes"]
                alerts.append({
                    "alert_id": alert["id"],
                    "route_id": route_id,
                    "header": attrs.get("header", ""),
                    "description": attrs.get("description", ""),
                    "severity": attrs.get("severity", 0),
                    "effect": attrs.get("effect", ""),
                    "created_at": attrs.get("created_at", ""),
                    "updated_at": attrs.get("updated_at", "")
                })
            
            return pd.DataFrame(alerts)
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return pd.DataFrame()

def main():
    """Test MBTA API integration"""
    mbta = MBTAAPI()
    
    print("Testing MBTA API...")
    
    # Get routes
    routes = mbta.get_routes()
    print(f"Found {len(routes)} routes")
    
    # Get vehicles for first route
    if not routes.empty:
        first_route = routes.iloc[0]["route_id"]
        vehicles = mbta.get_vehicles(first_route)
        print(f"Found {len(vehicles)} vehicles on route {first_route}")
    
    # Get alerts
    alerts = mbta.get_service_alerts()
    print(f"Found {len(alerts)} service alerts")

if __name__ == "__main__":
    main()
