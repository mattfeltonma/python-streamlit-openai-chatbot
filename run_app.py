#!/usr/bin/env python3
"""
Simple script to run the Streamlit chatbot application.
Usage: python run_app.py
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit application."""
    app_path = "app.py"
    
    if not os.path.exists(app_path):
        print(f"Error: {app_path} not found!")
        sys.exit(1)
    
    print("Starting Streamlit chatbot application...")
    print(f"App will be available at: http://localhost:8080")
    
    try:
        subprocess.run([
            "streamlit", "run", app_path, 
            "--server.port", "8080"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
    except FileNotFoundError:
        print("Error: Streamlit not found. Please install with: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()