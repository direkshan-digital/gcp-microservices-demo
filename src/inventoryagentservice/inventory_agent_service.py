#!/usr/bin/python
#
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import numpy as np
from scipy import stats
import requests

from flask import Flask, request, jsonify
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InventoryRecommendation:
    product_id: str
    current_stock: int
    recommended_stock: int
    reorder_point: int
    demand_forecast: float
    confidence_score: float
    reasoning: str
    external_factors: List[str]

@dataclass
class DemandForecast:
    product_id: str
    forecast_period_days: int
    predicted_demand: float
    confidence_interval: tuple
    trend_direction: str
    seasonality_factor: float
    external_signals: Dict[str, float]

class ExternalDataCollector:
    """Collects external signals that might affect demand"""
    
    def __init__(self):
        self.weather_api_key = os.environ.get("WEATHER_API_KEY", "")
        
    def get_weather_data(self, location: str = "general") -> Dict[str, Any]:
        """Get weather forecast data"""
        # Simulate weather data - in production would call actual weather API
        import random
        weather_conditions = ["sunny", "rainy", "cloudy", "snowy", "stormy"]
        temperature = random.randint(-10, 35)
        condition = random.choice(weather_conditions)
        
        return {
            "temperature": temperature,
            "condition": condition,
            "precipitation_chance": random.random(),
            "impact_score": self._calculate_weather_impact(condition, temperature)
        }
    
    def _calculate_weather_impact(self, condition: str, temperature: int) -> float:
        """Calculate how weather might impact shopping behavior"""
        impact_map = {
            "sunny": 0.1,
            "rainy": 0.3,
            "cloudy": 0.0,
            "snowy": 0.4,
            "stormy": 0.2
        }
        base_impact = impact_map.get(condition, 0.0)
        
        # Extreme temperatures increase indoor shopping
        if temperature < 0 or temperature > 30:
            base_impact += 0.2
            
        return min(base_impact, 1.0)
    
    def get_social_trends(self) -> Dict[str, float]:
        """Get social media trends that might affect product demand"""
        # Simulate social trend data
        import random
        trends = {
            "sustainable_fashion": random.random() * 0.5,
            "outdoor_activities": random.random() * 0.3,
            "work_from_home": random.random() * 0.4,
            "tech_accessories": random.random() * 0.6,
            "health_fitness": random.random() * 0.3
        }
        return trends
    
    def get_economic_indicators(self) -> Dict[str, float]:
        """Get economic indicators affecting consumer spending"""
        import random
        return {
            "consumer_confidence": random.uniform(0.3, 0.9),
            "unemployment_rate": random.uniform(0.03, 0.10),
            "inflation_rate": random.uniform(0.01, 0.05),
            "retail_spending_index": random.uniform(0.8, 1.2)
        }

class DemandForecastingEngine:
    """Advanced demand forecasting using multiple AI models"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        self.external_collector = ExternalDataCollector()
        
    def generate_mock_sales_data(self, product_id: str, days: int = 30) -> List[Dict]:
        """Generate realistic mock sales data for demonstration"""
        import random
        import math
        
        base_demand = random.randint(10, 100)
        data = []
        
        for i in range(days):
            # Add seasonality (weekly pattern)
            day_of_week = i % 7
            weekly_multiplier = 1.2 if day_of_week in [5, 6] else 0.9  # Weekend boost
            
            # Add trend
            trend = 1 + (i / days) * random.uniform(-0.3, 0.3)
            
            # Add noise
            noise = random.uniform(0.7, 1.3)
            
            demand = int(base_demand * weekly_multiplier * trend * noise)
            data.append({
                "date": (datetime.now() - timedelta(days=days-i)).isoformat(),
                "product_id": product_id,
                "sales": max(0, demand),
                "day_of_week": day_of_week
            })
            
        return data
    
    def forecast_demand(self, product_id: str, forecast_days: int = 7) -> DemandForecast:
        """Generate demand forecast using AI and external signals"""
        
        # Get historical sales data
        historical_data = self.generate_mock_sales_data(product_id, 30)
        
        # Get external signals
        weather_data = self.external_collector.get_weather_data()
        social_trends = self.external_collector.get_social_trends()
        economic_data = self.external_collector.get_economic_indicators()
        
        # Analyze historical patterns
        sales_values = [item["sales"] for item in historical_data]
        recent_sales = sales_values[-7:]  # Last week
        
        # Calculate trend
        x = np.arange(len(sales_values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, sales_values)
        trend_direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
        
        # Calculate seasonality (day of week effect)
        weekend_avg = np.mean([item["sales"] for item in historical_data if item["day_of_week"] in [5, 6]])
        weekday_avg = np.mean([item["sales"] for item in historical_data if item["day_of_week"] not in [5, 6]])
        seasonality_factor = weekend_avg / weekday_avg if weekday_avg > 0 else 1.0
        
        # Use AI to synthesize all signals
        ai_prompt = f"""
        As an expert demand forecasting AI, analyze the following data to predict demand for product {product_id}:
        
        Historical Sales (last 30 days): {sales_values}
        Recent Trend: {trend_direction} (slope: {slope:.3f})
        Seasonality Factor: {seasonality_factor:.2f}
        
        External Factors:
        - Weather: {weather_data}
        - Social Trends: {social_trends}
        - Economic Indicators: {economic_data}
        
        Provide a demand forecast for the next {forecast_days} days. Consider:
        1. Historical patterns and trends
        2. Seasonal effects
        3. External factor impacts
        4. Confidence level based on data quality
        
        Return your analysis as structured reasoning and a numerical forecast.
        """
        
        messages = [
            SystemMessage(content="You are an expert AI demand forecasting agent with access to multiple data sources."),
            HumanMessage(content=ai_prompt)
        ]
        
        ai_response = self.llm.invoke(messages)
        
        # Extract insights from AI response
        base_forecast = np.mean(recent_sales)
        
        # Apply external factor adjustments
        weather_impact = weather_data.get("impact_score", 0) * 0.2
        social_impact = sum(social_trends.values()) / len(social_trends) * 0.1
        economic_impact = economic_data.get("consumer_confidence", 0.5) * 0.15
        
        adjusted_forecast = base_forecast * (1 + weather_impact + social_impact + economic_impact)
        
        # Calculate confidence interval
        std_dev = np.std(sales_values)
        confidence_interval = (
            max(0, adjusted_forecast - 1.96 * std_dev),
            adjusted_forecast + 1.96 * std_dev
        )
        
        return DemandForecast(
            product_id=product_id,
            forecast_period_days=forecast_days,
            predicted_demand=adjusted_forecast,
            confidence_interval=confidence_interval,
            trend_direction=trend_direction,
            seasonality_factor=seasonality_factor,
            external_signals={
                "weather_impact": weather_impact,
                "social_impact": social_impact,
                "economic_impact": economic_impact
            }
        )

class InventoryOptimizer:
    """Optimizes inventory levels based on demand forecasts"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        
    def generate_recommendation(self, 
                                    product_id: str, 
                                    current_stock: int,
                                    demand_forecast: DemandForecast) -> InventoryRecommendation:
        """Generate inventory recommendation based on demand forecast"""
        
        # Calculate basic metrics
        safety_stock = max(5, int(demand_forecast.predicted_demand * 0.3))
        lead_time_demand = demand_forecast.predicted_demand * 0.5  # Assume 3.5 day lead time
        reorder_point = int(lead_time_demand + safety_stock)
        
        # Calculate recommended stock level
        forecast_uncertainty = abs(demand_forecast.confidence_interval[1] - demand_forecast.confidence_interval[0])
        buffer_stock = int(forecast_uncertainty * 0.2)
        recommended_stock = int(demand_forecast.predicted_demand * 1.5 + buffer_stock)
        
        # Use AI to provide reasoning
        reasoning_prompt = f"""
        As an inventory management AI agent, provide clear reasoning for inventory recommendations:
        
        Product: {product_id}
        Current Stock: {current_stock}
        Predicted Demand: {demand_forecast.predicted_demand:.1f}
        Confidence Interval: {demand_forecast.confidence_interval}
        Trend: {demand_forecast.trend_direction}
        External Factors: {demand_forecast.external_signals}
        
        Recommended Stock Level: {recommended_stock}
        Reorder Point: {reorder_point}
        
        Explain the reasoning behind these recommendations, considering:
        1. Demand forecast accuracy
        2. Risk of stockouts vs holding costs
        3. External factor impacts
        4. Trend analysis
        
        Provide a concise, business-friendly explanation.
        """
        
        messages = [
            SystemMessage(content="You are an expert inventory management AI that provides clear, actionable insights."),
            HumanMessage(content=reasoning_prompt)
        ]
        
        ai_reasoning = self.llm.invoke(messages)
        
        # Calculate confidence score
        forecast_accuracy = 1.0 - (forecast_uncertainty / demand_forecast.predicted_demand)
        confidence_score = min(0.95, max(0.1, forecast_accuracy * 0.8 + 0.2))
        
        # Identify key external factors
        external_factors = []
        for factor, impact in demand_forecast.external_signals.items():
            if abs(impact) > 0.1:
                direction = "increasing" if impact > 0 else "decreasing"
                external_factors.append(f"{factor} ({direction} demand)")
        
        return InventoryRecommendation(
            product_id=product_id,
            current_stock=current_stock,
            recommended_stock=recommended_stock,
            reorder_point=reorder_point,
            demand_forecast=demand_forecast.predicted_demand,
            confidence_score=confidence_score,
            reasoning=ai_reasoning.content,
            external_factors=external_factors
        )

class InventoryAgent:
    """Main agent orchestrating demand forecasting and inventory optimization"""
    
    def __init__(self):
        self.forecasting_engine = DemandForecastingEngine()
        self.optimizer = InventoryOptimizer()
        self.learning_data = []  # Store predictions vs actual for learning
        
    def process_product(self, product_id: str, current_stock: int) -> InventoryRecommendation:
        """Process a single product and generate inventory recommendation"""
        logger.info(f"Processing inventory analysis for product {product_id}")
        
        # Generate demand forecast
        demand_forecast = self.forecasting_engine.forecast_demand(product_id)
        
        # Generate inventory recommendation
        recommendation = self.optimizer.generate_recommendation(
            product_id, current_stock, demand_forecast
        )
        
        logger.info(f"Generated recommendation for {product_id}: {recommendation.recommended_stock} units")
        return recommendation
    
    def get_insights(self) -> Dict[str, Any]:
        """Get AI insights about inventory patterns and decisions"""
        insights_prompt = """
        As an inventory management AI agent, provide strategic insights about current inventory patterns:
        
        1. Overall inventory health
        2. Key trends observed across products
        3. External factors having the biggest impact
        4. Recommendations for inventory strategy improvements
        5. Areas where the AI model is most/least confident
        
        Provide actionable insights for inventory managers.
        """
        
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        messages = [
            SystemMessage(content="You are a strategic inventory management AI providing executive-level insights."),
            HumanMessage(content=insights_prompt)
        ]
        
        insights_response = llm.invoke(messages)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "insights": insights_response.content,
            "model_performance": {
                "total_predictions": len(self.learning_data),
                "avg_confidence": 0.75,  # Placeholder
                "last_updated": datetime.now().isoformat()
            }
        }

# Flask application
def create_app():
    app = Flask(__name__)
    agent = InventoryAgent()
    
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "healthy", "service": "inventoryagentservice"})
    
    @app.route("/forecast", methods=["POST"])
    def generate_forecast():
        """Generate demand forecast for a specific product"""
        data = request.get_json()
        product_id = data.get("product_id")
        forecast_days = data.get("forecast_days", 7)
        
        if not product_id:
            return jsonify({"error": "product_id is required"}), 400
        
        try:
            forecast = agent.forecasting_engine.forecast_demand(product_id, forecast_days)
            return jsonify(asdict(forecast))
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route("/inventory/recommendations", methods=["POST"])
    def get_inventory_recommendations():
        """Get inventory recommendations for products"""
        data = request.get_json()
        products = data.get("products", [])
        
        if not products:
            return jsonify({"error": "products list is required"}), 400
        
        try:
            recommendations = []
            for product_data in products:
                product_id = product_data.get("product_id")
                current_stock = product_data.get("current_stock", 0)
                
                if product_id:
                    recommendation = agent.process_product(product_id, current_stock)
                    recommendations.append(asdict(recommendation))
            
            return jsonify({"recommendations": recommendations})
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route("/agent/insights", methods=["GET"])
    def get_agent_insights():
        """Get AI insights about inventory patterns and decisions"""
        try:
            insights = agent.get_insights()
            return jsonify(insights)
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return jsonify({"error": str(e)}), 500
    
    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)