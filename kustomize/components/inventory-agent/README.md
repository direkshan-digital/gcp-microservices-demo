# Smart Inventory Demand Forecasting Agent

This component adds an autonomous AI agent for demand forecasting and inventory optimization to the Online Boutique application.

## Features

The Smart Inventory Agent provides:

- **Autonomous Decision Making**: Makes real-time inventory decisions without human intervention
- **Multi-Source Intelligence**: Combines internal sales data with external signals (weather, social trends, economic indicators)
- **Adaptive Learning**: Learns from prediction accuracy and adjusts models continuously
- **Explainable AI**: Provides clear reasoning for inventory decisions
- **Real-time Monitoring**: Continuously analyzes shopping patterns and external factors

## Architecture

The agent consists of several AI components:

1. **Pattern Recognition Engine**: Analyzes historical sales data
2. **External Signal Processor**: Monitors weather, social media trends, economic indicators
3. **Demand Forecasting Model**: Predicts future demand using multiple data sources
4. **Inventory Optimizer**: Recommends optimal stock levels and reorder points
5. **Learning Feedback Loop**: Continuously improves predictions

## API Endpoints

- `POST /forecast` - Generate demand forecast for specific products
- `POST /inventory/recommendations` - Get inventory recommendations for products
- `GET /agent/insights` - Get AI reasoning and insights for recent decisions
- `GET /health` - Health check endpoint

## Setup Instructions

1. Add the inventory-agent component to your kustomization.yaml:

```yaml
components:
- components/inventory-agent
```

2. Set the Google API key for Gemini:

```bash
export GOOGLE_API_KEY=<your_api_key>
sed -i "s/GOOGLE_API_KEY_VAL/${GOOGLE_API_KEY}/g" kustomize/components/inventory-agent/inventoryagentservice.yaml
```

3. Deploy the application:

```bash
kubectl apply -k .
```

## Usage Examples

### Generate Demand Forecast

```bash
curl -X POST http://inventoryagentservice:8080/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "OLJCESPC7Z",
    "forecast_days": 7
  }'
```

### Get Inventory Recommendations

```bash
curl -X POST http://inventoryagentservice:8080/inventory/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "products": [
      {"product_id": "OLJCESPC7Z", "current_stock": 50},
      {"product_id": "66VCHSJNUP", "current_stock": 25}
    ]
  }'
```

### Get AI Insights

```bash
curl -X GET http://inventoryagentservice:8080/agent/insights
```

## Example Response

```json
{
  "recommendations": [
    {
      "product_id": "OLJCESPC7Z",
      "current_stock": 50,
      "recommended_stock": 75,
      "reorder_point": 30,
      "demand_forecast": 42.5,
      "confidence_score": 0.82,
      "reasoning": "Based on increasing trend and upcoming weather changes...",
      "external_factors": ["weather_impact (increasing demand)", "seasonal_trend (weekend boost)"]
    }
  ]
}
```

## Integration with Online Boutique

The agent can be integrated with the existing microservices:

- **Product Catalog Service**: Get product information and categories
- **Cart Service**: Monitor real-time shopping behavior
- **Checkout Service**: Track completed purchases for learning
- **Frontend**: Display inventory insights and recommendations

## Environment Variables

- `GOOGLE_API_KEY`: API key for Gemini models
- `MODEL_UPDATE_INTERVAL`: How often to retrain models (default: 24h)
- `WEATHER_API_KEY`: API key for weather data (optional)
- `EXTERNAL_DATA_SOURCES`: Comma-separated list of data sources to monitor