#!/usr/bin/env python3
"""
MCP Weather Server - A Model Context Protocol server for weather data
Provides tools for getting weather information and forecasts
"""

import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

# Load environment variables
load_dotenv()

# Environment variables
API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable is required")

# OpenWeatherMap API URLs
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"
GEOCODING_URL = "http://api.openweathermap.org/geo/1.0/direct"
AIR_POLLUTION_URL = "http://api.openweathermap.org/data/2.5/air_pollution"

# Popular cities for resources
POPULAR_CITIES = ["New York", "London", "Tokyo", "Paris", "Sydney", "Los Angeles", "Berlin"]

# Create the server
server = Server("weather-server")

def get_coordinates_for_city(city):
    """Get coordinates for a city using OpenWeatherMap Geocoding API"""
    try:
        params = {
            'q': city,
            'limit': 1,
            'appid': API_KEY
        }
        response = requests.get(GEOCODING_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                location = data[0]
                return {
                    'lat': location['lat'],
                    'lon': location['lon'],
                    'name': location['name'],
                    'country': location.get('country', '')
                }
        return None
    except Exception as e:
        print(f"Geocoding API Error: {e}")
        return None

def get_air_quality_data(lat, lon):
    """Get air quality data for coordinates"""
    try:
        params = {
            'lat': lat,
            'lon': lon,
            'appid': API_KEY
        }
        response = requests.get(AIR_POLLUTION_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            aqi = data['list'][0]['main']['aqi']
            
            # AQI levels: 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor
            aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
            aqi_colors = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "🟣"}
            
            return {
                'aqi': aqi,
                'aqi_label': aqi_labels.get(aqi, "Unknown"),
                'aqi_color': aqi_colors.get(aqi, "⚪")
            }
    except Exception as e:
        print(f"Air Quality API Error: {e}")
        return None

def get_weather_data(city, units='metric'):
    """Get comprehensive weather data for a city"""
    try:
        # First try direct city search
        params = {
            'q': city,
            'appid': API_KEY,
            'units': units
        }
        response = requests.get(WEATHER_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            temp_unit = '°F' if units == 'imperial' else '°C'
            speed_unit = 'mph' if units == 'imperial' else 'm/s'
            
            # Get air quality data
            air_quality = get_air_quality_data(data['coord']['lat'], data['coord']['lon'])
            
            # Format sunrise/sunset times
            sunrise_ts = data['sys'].get('sunrise', 0)
            sunset_ts = data['sys'].get('sunset', 0)
            sunrise_time = datetime.fromtimestamp(sunrise_ts).strftime('%H:%M') if sunrise_ts else '--:--'
            sunset_time = datetime.fromtimestamp(sunset_ts).strftime('%H:%M') if sunset_ts else '--:--'
            
            # Convert wind speed for imperial units
            wind_speed = data.get('wind', {}).get('speed', 0)
            if units == 'imperial':
                wind_speed = wind_speed * 2.237  # Convert m/s to mph
            
            result = {
                'temperature': data['main']['temp'],
                'temp_unit': temp_unit,
                'feels_like': data['main']['feels_like'],
                'condition': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': wind_speed,
                'wind_unit': speed_unit,
                'wind_direction': data.get('wind', {}).get('deg', 0),
                'clouds': data.get('clouds', {}).get('all', 0),
                'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                'pressure': data['main'].get('pressure', 0),
                'sunrise': sunrise_time,
                'sunset': sunset_time,
                'city': data['name'],
                'country': data['sys']['country'],
                'coordinates': {
                    'lat': data['coord']['lat'],
                    'lon': data['coord']['lon']
                }
            }
            
            # Add air quality if available
            if air_quality:
                result.update({
                    'aqi': air_quality['aqi'],
                    'aqi_label': air_quality['aqi_label'],
                    'aqi_color': air_quality['aqi_color']
                })
            
            return result
        else:
            # Geocoding fallback
            coordinates = get_coordinates_for_city(city)
            if coordinates:
                coord_params = {
                    'lat': coordinates['lat'],
                    'lon': coordinates['lon'],
                    'appid': API_KEY,
                    'units': units
                }
                coord_response = requests.get(WEATHER_URL, params=coord_params, timeout=10)
                
                if coord_response.status_code == 200:
                    # Same processing as above...
                    data = coord_response.json()
                    temp_unit = '°F' if units == 'imperial' else '°C'
                    speed_unit = 'mph' if units == 'imperial' else 'm/s'
                    
                    air_quality = get_air_quality_data(coordinates['lat'], coordinates['lon'])
                    
                    sunrise_ts = data['sys'].get('sunrise', 0)
                    sunset_ts = data['sys'].get('sunset', 0)
                    sunrise_time = datetime.fromtimestamp(sunrise_ts).strftime('%H:%M') if sunrise_ts else '--:--'
                    sunset_time = datetime.fromtimestamp(sunset_ts).strftime('%H:%M') if sunset_ts else '--:--'
                    
                    wind_speed = data.get('wind', {}).get('speed', 0)
                    if units == 'imperial':
                        wind_speed = wind_speed * 2.237
                    
                    result = {
                        'temperature': data['main']['temp'],
                        'temp_unit': temp_unit,
                        'feels_like': data['main']['feels_like'],
                        'condition': data['weather'][0]['description'],
                        'humidity': data['main']['humidity'],
                        'wind_speed': wind_speed,
                        'wind_unit': speed_unit,
                        'wind_direction': data.get('wind', {}).get('deg', 0),
                        'clouds': data.get('clouds', {}).get('all', 0),
                        'visibility': data.get('visibility', 0) / 1000,
                        'pressure': data['main'].get('pressure', 0),
                        'sunrise': sunrise_time,
                        'sunset': sunset_time,
                        'city': coordinates['name'],
                        'country': coordinates['country'],
                        'coordinates': {
                            'lat': coordinates['lat'],
                            'lon': coordinates['lon']
                        }
                    }
                    
                    if air_quality:
                        result.update({
                            'aqi': air_quality['aqi'],
                            'aqi_label': air_quality['aqi_label'],
                            'aqi_color': air_quality['aqi_color']
                        })
                    
                    return result
            return None
    except Exception as e:
        print(f"Weather API Error: {e}")
        return None

def get_forecast_data(city, units='metric'):
    """Get 5-day weather forecast for a city"""
    try:
        coordinates = get_coordinates_for_city(city)
        if not coordinates:
            return None
        
        params = {
            'lat': coordinates['lat'],
            'lon': coordinates['lon'],
            'appid': API_KEY,
            'units': units
        }
        response = requests.get(FORECAST_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            temp_unit = '°F' if units == 'imperial' else '°C'
            
            daily_forecasts = []
            seen_dates = set()
            
            for item in data['list']:
                date_str = item['dt_txt'][:10]
                time_str = item['dt_txt'][11:13]
                
                if date_str not in seen_dates and time_str in ['12', '15']:
                    seen_dates.add(date_str)
                    
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%a, %b %d')
                    
                    daily_forecasts.append({
                        'date': formatted_date,
                        'temperature': item['main']['temp'],
                        'temp_unit': temp_unit,
                        'condition': item['weather'][0]['description'],
                        'humidity': item['main']['humidity'],
                        'wind_speed': item.get('wind', {}).get('speed', 0)
                    })
                    
                    if len(daily_forecasts) >= 5:
                        break
            
            return {
                'city': coordinates['name'],
                'country': coordinates['country'],
                'forecasts': daily_forecasts
            }
        else:
            return None
            
    except Exception as e:
        print(f"Forecast API Error: {e}")
        return None

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available weather resources"""
    resources = []
    
    # Add popular cities as resources
    for city in POPULAR_CITIES:
        resources.append(
            Resource(
                uri=f"weather://{city.lower().replace(' ', '-')}",
                name=f"Weather for {city}",
                description=f"Current weather conditions and forecast for {city}",
                mimeType="application/json"
            )
        )
    
    # Add general resources
    resources.append(
        Resource(
            uri="weather://search",
            name="Weather Search",
            description="Search for weather information for any city worldwide",
            mimeType="application/json"
        )
    )
    
    return resources

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read weather resource data"""
    if uri.startswith("weather://"):
        city_slug = uri.replace("weather://", "")
        
        if city_slug == "search":
            return json.dumps({
                "description": "Use the get_weather or get_forecast tools to search for weather data",
                "available_tools": ["get_weather", "get_forecast", "search_cities"],
                "popular_cities": POPULAR_CITIES
            })
        
        # Convert slug back to city name
        city = city_slug.replace('-', ' ').title()
        
        # Get weather data for the city
        weather_data = get_weather_data(city)
        if weather_data:
            return json.dumps(weather_data, indent=2)
        else:
            return json.dumps({"error": f"Could not fetch weather data for {city}"})
    
    raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available weather tools"""
    return [
        Tool(
            name="get_weather",
            description="Get current weather conditions for a specific city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city to get weather for"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "description": "Temperature units (metric for Celsius, imperial for Fahrenheit)",
                        "default": "metric"
                    }
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="get_forecast",
            description="Get 5-day weather forecast for a specific city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city to get forecast for"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "description": "Temperature units (metric for Celsius, imperial for Fahrenheit)",
                        "default": "metric"
                    }
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="search_cities",
            description="Search for cities and get their coordinates using geocoding",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "City name or partial name to search for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""
    
    if name == "get_weather":
        city = arguments.get("city")
        units = arguments.get("units", "metric")
        
        if not city:
            return [TextContent(type="text", text="Error: City name is required")]
        
        weather_data = get_weather_data(city, units)
        if weather_data:
            # Format the response nicely
            temp_display = f"{int(weather_data['temperature'])}{weather_data['temp_unit']}"
            feels_like_display = f"{int(weather_data['feels_like'])}{weather_data['temp_unit']}"
            wind_display = f"{weather_data['wind_speed']:.1f} {weather_data['wind_unit']}"
            
            response = f"""🌤️ Weather for {weather_data['city']}, {weather_data['country']}

🌡️ Temperature: {temp_display} (feels like {feels_like_display})
☁️ Conditions: {weather_data['condition'].title()}
💧 Humidity: {weather_data['humidity']}%
💨 Wind: {wind_display} ({weather_data['wind_direction']}°)
☁️ Clouds: {weather_data['clouds']}%
👁️ Visibility: {weather_data['visibility']:.1f} km
🔽 Pressure: {weather_data['pressure']} hPa
🌅 Sunrise: {weather_data['sunrise']}
🌇 Sunset: {weather_data['sunset']}"""
            
            if 'aqi' in weather_data:
                response += f"\n🍃 Air Quality: {weather_data['aqi_color']} {weather_data['aqi_label']} (AQI: {weather_data['aqi']})"
            
            return [TextContent(type="text", text=response)]
        else:
            return [TextContent(type="text", text=f"❌ Could not find weather data for '{city}'. Please check the city name and try again.")]
    
    elif name == "get_forecast":
        city = arguments.get("city")
        units = arguments.get("units", "metric")
        
        if not city:
            return [TextContent(type="text", text="Error: City name is required")]
        
        forecast_data = get_forecast_data(city, units)
        if forecast_data:
            response = f"📅 5-Day Forecast for {forecast_data['city']}, {forecast_data['country']}\n\n"
            
            for forecast in forecast_data['forecasts']:
                temp_display = f"{int(forecast['temperature'])}{forecast['temp_unit']}"
                response += f"📆 {forecast['date']}\n"
                response += f"   🌡️ {temp_display} - {forecast['condition'].title()}\n"
                response += f"   💧 {forecast['humidity']}% humidity, 💨 {forecast['wind_speed']:.1f} m/s wind\n\n"
            
            return [TextContent(type="text", text=response)]
        else:
            return [TextContent(type="text", text=f"❌ Could not find forecast data for '{city}'. Please check the city name and try again.")]
    
    elif name == "search_cities":
        query = arguments.get("query")
        limit = arguments.get("limit", 5)
        
        if not query:
            return [TextContent(type="text", text="Error: Search query is required")]
        
        try:
            params = {
                'q': query,
                'limit': limit,
                'appid': API_KEY
            }
            response = requests.get(GEOCODING_URL, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    result = f"🔍 Found {len(data)} cities matching '{query}':\n\n"
                    
                    for i, location in enumerate(data, 1):
                        city_name = location['name']
                        country = location.get('country', '')
                        state = location.get('state', '')
                        lat = location.get('lat', 0)
                        lon = location.get('lon', 0)
                        
                        display_name = city_name
                        if state and country:
                            display_name = f"{city_name}, {state}, {country}"
                        elif country:
                            display_name = f"{city_name}, {country}"
                        
                        result += f"{i}. {display_name}\n"
                        result += f"   📍 Coordinates: {lat:.2f}, {lon:.2f}\n\n"
                    
                    return [TextContent(type="text", text=result)]
                else:
                    return [TextContent(type="text", text=f"🔍 No cities found matching '{query}'. Try a different search term.")]
            else:
                return [TextContent(type="text", text="❌ Error searching for cities. Please try again.")]
        
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Search error: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]

async def main():
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="weather-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())