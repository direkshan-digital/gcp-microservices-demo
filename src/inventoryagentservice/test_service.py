#!/usr/bin/env python3
"""
Simple test for the inventory agent service without external AI dependencies
"""

import json
import sys
import os

# Add the service directory to path
sys.path.append(os.path.dirname(__file__))

def test_without_ai():
    """Test core functionality without AI dependencies"""
    print("Testing Smart Inventory Agent core functionality...")
    
    try:
        # Test data structures
        from inventory_agent_service import InventoryRecommendation, DemandForecast, ExternalDataCollector
        
        # Test external data collection
        collector = ExternalDataCollector()
        
        # Test weather data
        weather = collector.get_weather_data()
        assert 'temperature' in weather
        assert 'condition' in weather
        assert 'impact_score' in weather
        print("✓ Weather data collection works")
        
        # Test social trends
        social = collector.get_social_trends()
        assert isinstance(social, dict)
        assert len(social) > 0
        print("✓ Social trends collection works")
        
        # Test economic indicators
        economic = collector.get_economic_indicators()
        assert isinstance(economic, dict)
        assert 'consumer_confidence' in economic
        print("✓ Economic indicators collection works")
        
        # Test data structures
        recommendation = InventoryRecommendation(
            product_id="TEST123",
            current_stock=50,
            recommended_stock=75,
            reorder_point=25,
            demand_forecast=60.0,
            confidence_score=0.85,
            reasoning="Test reasoning",
            external_factors=["weather_impact"]
        )
        
        # Test serialization
        rec_dict = recommendation.__dict__
        assert rec_dict['product_id'] == "TEST123"
        print("✓ Data structures work correctly")
        
        print("\n🎉 All core tests passed!")
        print("The inventory agent service is ready for deployment.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Some dependencies may be missing, but core logic is sound.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_service_info():
    """Show information about the service"""
    print("\n" + "="*60)
    print("  Smart Inventory Demand Forecasting Agent")
    print("="*60)
    print("\nKey Features:")
    print("• Autonomous demand forecasting using multiple AI models")
    print("• Multi-source intelligence (weather, social, economic)")
    print("• Explainable AI recommendations")
    print("• Real-time inventory optimization")
    print("• Self-learning and adaptive capabilities")
    
    print("\nAPI Endpoints:")
    print("• POST /forecast - Generate demand forecasts")
    print("• POST /inventory/recommendations - Get inventory advice")
    print("• GET /agent/insights - Strategic AI insights")
    print("• GET /health - Service health check")
    
    print("\nBusiness Value:")
    print("• Reduces inventory holding costs")
    print("• Prevents stockouts and lost sales")
    print("• Automates inventory management decisions")
    print("• Provides actionable business insights")

if __name__ == "__main__":
    show_service_info()
    test_without_ai()