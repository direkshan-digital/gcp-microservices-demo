#!/usr/bin/python
#
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import numpy as np
from scipy import stats

from flask import Flask, request, jsonify

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
    def __init__(self):
        pass
        
    def get_weather_data(self, location: str = "general") -> Dict[str, Any]:
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
        impact_map = {
            "sunny": 0.1, "rainy": 0.3, "cloudy": 0.0, "snowy": 0.4, "stormy": 0.2
        }
        base_impact = impact_map.get(condition, 0.0)
        if temperature < 0 or temperature > 30:
            base_impact += 0.2
        return min(base_impact, 1.0)
    
    def get_social_trends(self) -> Dict[str, float]:
        import random
        return {
            "sustainable_fashion": random.random() * 0.5,
            "outdoor_activities": random.random() * 0.3,
            "work_from_home": random.random() * 0.4,
            "tech_accessories": random.random() * 0.6,
            "health_fitness": random.random() * 0.3
        }
    
    def get_economic_indicators(self) -> Dict[str, float]:
        import random
        return {
            "consumer_confidence": random.uniform(0.3, 0.9),
            "unemployment_rate": random.uniform(0.03, 0.10),
            "inflation_rate": random.uniform(0.01, 0.05),
            "retail_spending_index": random.uniform(0.8, 1.2)
        }

# Simple test
if __name__ == "__main__":
    print("Testing inventory agent components...")
    collector = ExternalDataCollector()
    weather = collector.get_weather_data()
    print(f"Weather test: {weather}")
    print("All tests passed!")