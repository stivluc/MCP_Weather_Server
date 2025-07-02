#!/usr/bin/env python3
"""
Run the MCP Weather Server directly
"""

import asyncio
import sys
import os
from mcp_weather_server import main

if __name__ == "__main__":
    # Ensure we have the API key
    if not os.environ.get('API_KEY'):
        print("Error: API_KEY environment variable is required", file=sys.stderr)
        sys.exit(1)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)