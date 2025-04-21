#!/usr/bin/env python3
"""
Script to start the AWS Cost Calculator

This script starts the Streamlit application for the AWS Cost Calculator.
"""
import os
import subprocess
import sys


def main():
    """
    Main function to start the Streamlit application
    """
    print("Starting AWS Cost Calculator...")

    # Check if virtual environment is activated
    if not os.environ.get("VIRTUAL_ENV"):
        print(
            "WARNING: Virtual environment not detected. We recommend using a virtual environment."
        )
        print("You can create a virtual environment with: python -m venv venv")
        print(
            "And activate it with: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
        )

        # Ask if the user wants to continue without a virtual environment
        if (
            input(
                "Do you want to continue without a virtual environment? (y/n): "
            ).lower()
            != "y"
        ):
            print("Exiting...")
            sys.exit(0)

    # Check if dependencies are installed
    try:
        import streamlit
        import boto3
        import pandas
    except ImportError:
        print("Some dependencies are not installed. Installing now...")
        subprocess.call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )

    # Start the Streamlit application
    script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "src", "app.py"
    )
    subprocess.call(["streamlit", "run", script_path])


if __name__ == "__main__":
    main()
