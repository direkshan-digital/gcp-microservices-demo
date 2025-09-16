#!/usr/bin/env python3
"""
Demo script for the Smart Inventory Demand Forecasting Agent

This script demonstrates the capabilities of the inventory agent by:
1. Starting the agent service
2. Making API calls to show different features
3. Displaying the results in a user-friendly format
"""

import requests
import json
import time
import threading
import subprocess
import sys
from datetime import datetime

# Configuration
SERVICE_URL = "http://localhost:8080"
DEMO_PRODUCTS = [
    {"product_id": "OLJCESPC7Z", "name": "Sunglasses", "current_stock": 45},
    {"product_id": "66VCHSJNUP", "name": "Tank Top", "current_stock": 23},
    {"product_id": "1YMWWN1N4O", "name": "Watch", "current_stock": 67},
    {"product_id": "L9ECAV7KIM", "name": "Loafers", "current_stock": 12},
    {"product_id": "2ZYFJ3GM2N", "name": "Vintage Camera", "current_stock": 8}
]

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section"""
    print(f"\n--- {title} ---")

def wait_for_service(url, timeout=30):
    """Wait for the service to be ready"""
    print("Waiting for inventory agent service to start...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=2)
            if response.status_code == 200:
                print("✓ Service is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    
    print("✗ Service failed to start within timeout")
    return False

def demo_health_check():
    """Demonstrate health check endpoint"""
    print_section("Health Check")
    try:
        response = requests.get(f"{SERVICE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Service Status: {data['status']}")
            print(f"✓ Service Name: {data['service']}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")

def demo_demand_forecast():
    """Demonstrate demand forecasting for individual products"""
    print_section("Demand Forecasting")
    
    for product in DEMO_PRODUCTS[:3]:  # Demo first 3 products
        print(f"\n📊 Forecasting demand for {product['name']} ({product['product_id']})")
        
        try:
            payload = {
                "product_id": product["product_id"],
                "forecast_days": 7
            }
            
            response = requests.post(f"{SERVICE_URL}/forecast", json=payload, timeout=30)
            
            if response.status_code == 200:
                forecast = response.json()
                print(f"   • Predicted Demand: {forecast['predicted_demand']:.1f} units")
                print(f"   • Confidence Range: {forecast['confidence_interval'][0]:.1f} - {forecast['confidence_interval'][1]:.1f}")
                print(f"   • Trend: {forecast['trend_direction']}")
                print(f"   • Seasonality Factor: {forecast['seasonality_factor']:.2f}")
                
                # Show external signals
                signals = forecast['external_signals']
                print(f"   • External Factors:")
                for signal, impact in signals.items():
                    direction = "↑" if impact > 0 else "↓" if impact < 0 else "→"
                    print(f"     - {signal}: {direction} {abs(impact):.3f}")
            else:
                print(f"   ✗ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        time.sleep(1)  # Small delay between requests

def demo_inventory_recommendations():
    """Demonstrate inventory recommendations"""
    print_section("Inventory Recommendations")
    
    try:
        payload = {"products": DEMO_PRODUCTS}
        response = requests.post(f"{SERVICE_URL}/inventory/recommendations", json=payload, timeout=45)
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data["recommendations"]
            
            print(f"\n🎯 Generated recommendations for {len(recommendations)} products:\n")
            
            for rec in recommendations:
                print(f"📦 {rec['product_id']}")
                print(f"   Current Stock: {rec['current_stock']} units")
                print(f"   Recommended: {rec['recommended_stock']} units")
                print(f"   Reorder Point: {rec['reorder_point']} units")
                print(f"   Demand Forecast: {rec['demand_forecast']:.1f} units")
                print(f"   Confidence: {rec['confidence_score']:.0%}")
                
                if rec['external_factors']:
                    print(f"   External Factors: {', '.join(rec['external_factors'])}")
                
                # Show action needed
                current = rec['current_stock']
                recommended = rec['recommended_stock']
                reorder = rec['reorder_point']
                
                if current <= reorder:
                    print(f"   🚨 ACTION NEEDED: Stock below reorder point!")
                elif current < recommended:
                    print(f"   ⚠️  CONSIDER: Increase stock by {recommended - current} units")
                else:
                    print(f"   ✅ STOCK OK: Current levels sufficient")
                
                print()
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"✗ Error: {e}")

def demo_agent_insights():
    """Demonstrate AI insights"""
    print_section("Agent Insights & Strategic Analysis")
    
    try:
        response = requests.get(f"{SERVICE_URL}/agent/insights", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"🧠 AI Strategic Insights (Generated: {data['timestamp']})\n")
            print(data['insights'])
            
            # Show model performance
            perf = data['model_performance']
            print(f"\n📊 Model Performance:")
            print(f"   • Total Predictions: {perf['total_predictions']}")
            print(f"   • Average Confidence: {perf['avg_confidence']:.0%}")
            print(f"   • Last Updated: {perf['last_updated']}")
        else:
            print(f"✗ Error: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error: {e}")

def run_demo():
    """Run the complete demo"""
    print_header("Smart Inventory Demand Forecasting Agent - Demo")
    print("This demo showcases an autonomous AI agent that:")
    print("• Analyzes sales patterns and external factors")
    print("• Predicts future demand using multiple AI models")
    print("• Provides intelligent inventory recommendations")
    print("• Explains its reasoning in business-friendly terms")
    
    # Check if service is running
    try:
        demo_health_check()
    except requests.exceptions.ConnectionError:
        print("\n❌ Service not running. Please start the inventory agent service first:")
        print("   cd src/inventoryagentservice")
        print("   python inventory_agent_service.py")
        return
    
    # Run demo sections
    demo_demand_forecast()
    demo_inventory_recommendations()
    demo_agent_insights()
    
    print_header("Demo Complete")
    print("🎉 The Smart Inventory Agent has successfully demonstrated:")
    print("✓ Multi-source demand forecasting")
    print("✓ Intelligent inventory optimization")
    print("✓ Explainable AI reasoning")
    print("✓ Real-time external factor analysis")
    print("\nThis agent provides autonomous, data-driven inventory management")
    print("that can significantly reduce costs while preventing stockouts!")

if __name__ == "__main__":
    run_demo()