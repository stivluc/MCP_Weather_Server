# 🌤️ MCP Weather Server

A **Model Context Protocol (MCP)** server that provides weather data tools and resources using OpenWeatherMap API.

## 🎯 What is MCP?

**Model Context Protocol (MCP)** is a standardized way for AI assistants to connect to external tools and data sources. This weather server implements the MCP protocol to provide:

- 🛠️ **MCP Tools**: `get_weather`, `get_forecast`, `search_cities`
- 📚 **MCP Resources**: Weather data for popular cities and search functionality
- 🔄 **Real-time Data**: Live weather information from OpenWeatherMap API
- 📊 **Structured Access**: JSON-based weather data through MCP protocol

## ✨ MCP Features

### Tools Available

- **get_weather**: Get current weather conditions for any city
- **get_forecast**: Get 5-day weather forecast for any city
- **search_cities**: Search and geocode cities worldwide

### Resources Available

- **weather://new-york**: Weather data for New York
- **weather://london**: Weather data for London
- **weather://tokyo**: Weather data for Tokyo
- **weather://paris**: Weather data for Paris
- **weather://sydney**: Weather data for Sydney
- **weather://los-angeles**: Weather data for Los Angeles
- **weather://berlin**: Weather data for Berlin
- **weather://search**: General search functionality

## 🚀 Quick Start

### Running the MCP Server

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/mcp-weather-server.git
cd mcp-weather-server
```

2. **Create virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set API key**

```bash
export API_KEY=your_openweathermap_api_key_here
```

5. **Run the MCP server**

```bash
python run_mcp_server.py
```

### Using with Claude Desktop

Add this configuration to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/path/to/your/project/mcp_weather_server.py"],
      "env": {
        "API_KEY": "your_openweathermap_api_key_here"
      }
    }
  }
}
```

### Get OpenWeatherMap API Key

1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key
3. Use it in the environment variable `API_KEY`

## 🏗️ MCP Architecture

- **Protocol**: Model Context Protocol (MCP) over stdio
- **Transport**: JSON-RPC communication
- **Server**: Python with mcp library
- **API**: OpenWeatherMap for weather data and geocoding
- **Tools**: 3 MCP tools (get_weather, get_forecast, search_cities)
- **Resources**: 8 MCP resources (popular cities + search)

## 📁 Project Structure

```
mcp-weather-server/
├── mcp_weather_server.py    # Main MCP server implementation
├── run_mcp_server.py        # Server runner script
├── mcp_config.json         # MCP configuration example
├── requirements.txt        # Python dependencies (mcp library)
├── app.py                  # Legacy Flask app (for reference)
├── README.md              # This file
└── .env                   # Environment variables (API_KEY)
```

## 🔧 MCP Tools Usage

### get_weather Tool

```json
{
  "name": "get_weather",
  "arguments": {
    "city": "London",
    "units": "metric"
  }
}
```

### get_forecast Tool

```json
{
  "name": "get_forecast",
  "arguments": {
    "city": "Tokyo",
    "units": "imperial"
  }
}
```

### search_cities Tool

```json
{
  "name": "search_cities",
  "arguments": {
    "query": "New York",
    "limit": 5
  }
}
```

## 📚 MCP Resources Access

Resources can be accessed via URI patterns:

- `weather://new-york` - Weather data for New York
- `weather://london` - Weather data for London
- `weather://search` - General search information

## 🛡️ Security

- ✅ API keys properly externalized via environment variables
- ✅ MCP server runs in isolated process
- ✅ Input validation on all tool parameters
- ✅ Error handling for API failures
- ✅ No hardcoded secrets in repository

## 🧪 Testing the MCP Server

You can test the server functionality by running it directly:

```bash
# Test the server
python run_mcp_server.py

# The server communicates via stdio using JSON-RPC
# It's designed to be used by MCP clients like Claude Desktop
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes (ensure MCP protocol compliance)
4. Test with MCP clients
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🎉 MCP Features in Action

1. **Tool Integration** → AI can call weather tools directly
2. **Resource Access** → Structured weather data via URIs
3. **Real-time Data** → Live weather information through MCP
4. **Error Handling** → Graceful MCP error responses
5. **Protocol Compliance** → Full MCP specification support

---

**Built to learn about MCP.**
