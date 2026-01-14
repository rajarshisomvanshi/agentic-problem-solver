#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Server Startup Script
"""

import os
import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Start the server"""
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    print(f"🚀 Starting Agentic Problem Solver API")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"   Reload: {reload}")

    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


if __name__ == "__main__":
    main()
