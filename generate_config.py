#!/usr/bin/env python3
"""
Generate Claude Desktop configuration for Nutrition MCP Server
"""

import json
import os
import sys
from pathlib import Path


def get_current_directory():
    """Get the absolute path of the current directory"""
    return os.path.abspath(os.getcwd())


def generate_config():
    """Generate Claude Desktop configuration"""
    current_dir = get_current_directory()
    python_path = os.path.join(current_dir, "nutrition-env", "bin", "python")
    main_path = os.path.join(current_dir, "main.py")

    # Check if files exist
    if not os.path.exists(python_path):
        print("❌ Virtual environment not found. Run: python3 -m venv nutrition-env")
        sys.exit(1)

    if not os.path.exists(main_path):
        print("❌ main.py not found in current directory")
        sys.exit(1)

    config = {
        "mcpServers": {
            "nutrition": {
                "command": python_path,
                "args": [main_path],
                "env": {"USDA_API_KEY": "YOUR_API_KEY_HERE"},
            }
        }
    }

    return config


def get_config_path():
    """Get Claude Desktop config file path"""
    home = Path.home()
    if sys.platform == "darwin":  # macOS
        return (
            home
            / "Library"
            / "Application Support"
            / "Claude"
            / "claude_desktop_config.json"
        )
    elif sys.platform == "win32":  # Windows
        return Path(os.getenv("APPDATA")) / "Claude" / "claude_desktop_config.json"
    else:
        print("❌ Unsupported platform. Manual config required.")
        return None


def main():
    print("🔧 Generating Claude Desktop configuration...")

    config = generate_config()
    config_path = get_config_path()

    print("\n📋 Configuration to add to Claude Desktop:")
    print("=" * 50)
    print(json.dumps(config, indent=2))
    print("=" * 50)

    if config_path:
        print(f"\n📁 Config file location:")
        print(f"file://{config_path}")

        # Check if config file exists
        if config_path.exists():
            print("⚠️  Config file exists. You'll need to merge this configuration.")
        else:
            print("ℹ️  Config file doesn't exist. Create it with the above content.")

    print("\n⚠️  Remember to:")
    print("1. Replace 'YOUR_API_KEY_HERE' with your actual USDA API key")
    print("2. Get free key at: https://fdc.nal.usda.gov/api-guide.html")
    print("3. Restart Claude Desktop after saving config")


if __name__ == "__main__":
    main()
