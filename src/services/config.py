#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration loader for the application
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load YAML configuration file"""
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "main.yaml"
    
    config_path = Path(config_path)
    
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config or {}
    
    return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """Get default configuration"""
    return {
        "system": {
            "language": "en",
            "output_base_dir": "./data/user/solve",
        },
        "solve": {
            "max_steps": 5,
            "max_retries": 2,
            "timeout": 300,
            "save_intermediate_results": True,
            "agents": {
                "manager_agent": {
                    "temperature": 0.4,
                    "max_tokens": 4000,
                },
                "solve_agent": {
                    "temperature": 0.7,
                    "max_tokens": 8192,
                },
                "response_agent": {
                    "temperature": 0.5,
                    "max_tokens": 4096,
                },
            },
        },
        "llm": {
            "model": "gpt-4-turbo",
            "temperature": 0.7,
            "max_tokens": 4000,
            "timeout": 120,
        },
        "logging": {
            "level": "INFO",
            "log_dir": "./logs",
            "console_output": True,
            "save_to_file": True,
        },
    }


def get_agent_config(config: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
    """Get specific agent configuration"""
    solve_config = config.get("solve", {})
    agents_config = solve_config.get("agents", {})
    return agents_config.get(agent_name, {})
