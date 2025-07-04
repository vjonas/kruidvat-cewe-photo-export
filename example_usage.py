#!/usr/bin/env python3
"""
Example usage of both fetch_photobook.py and create_spreads.py
This script demonstrates how to fetch a photo book and create spreads
"""

import os
import sys
import subprocess
import time

def run_command(cmd):
    """Run a command and return the result"""
    print(f"🔧 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Success!")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ Error: {result.stderr}")
        return False
    
    return True

def main():
    print("🎉 Photo Book Fetcher & Spread Creator Example")
    print("=" * 50)
    
    # Check if required files exist
    if not os.path.exists("fetch_photobook.py"):
        print("❌ Error: fetch_photobook.py not found!")
        sys.exit(1)
    
    if not os.path.exists("create_spreads.py"):
        print("❌ Error: create_spreads.py not found!")
        sys.exit(1)
    
    print("\n📚 Step 1: Fetching photo book pages...")
    # Fetch first 10 pages as example (you can change this)
    if not run_command(["python", "fetch_photobook.py", "1", "10"]):
        print("❌ Failed to fetch photo book pages")
        sys.exit(1)
    
    # Check if PDF was created
    pdf_path = "output/oma_jeanne_photobook.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ Error: Expected PDF not found at {pdf_path}")
        sys.exit(1)
    
    print(f"\n📖 Step 2: Creating spreads from {pdf_path}...")
    # Create spreads starting from page 2
    if not run_command(["python", "create_spreads.py", pdf_path, "-s", "2"]):
        print("❌ Failed to create spreads")
        sys.exit(1)
    
    # Check if spread PDF was created
    spread_pdf_path = "output/oma_jeanne_photobook_spreads.pdf"
    if os.path.exists(spread_pdf_path):
        print(f"\n🎉 Success! Both PDFs created:")
        print(f"   📄 Original: {pdf_path}")
        print(f"   📖 Spreads: {spread_pdf_path}")
        
        # Show file sizes
        original_size = os.path.getsize(pdf_path) / (1024 * 1024)
        spread_size = os.path.getsize(spread_pdf_path) / (1024 * 1024)
        
        print(f"\n📊 File sizes:")
        print(f"   Original: {original_size:.2f} MB")
        print(f"   Spreads: {spread_size:.2f} MB")
    else:
        print(f"❌ Error: Spread PDF not found at {spread_pdf_path}")
        sys.exit(1)
    
    print("\n✨ Example completed successfully!")
    print("\nTo run with your full photo book:")
    print("1. python fetch_photobook.py                    # Fetch all pages")
    print("2. python create_spreads.py output/oma_jeanne_photobook.pdf  # Create spreads")

if __name__ == "__main__":
    main() 