#!/usr/bin/env python3
"""
Build verification script to ensure all dependencies are properly installed.
"""
import sys
import subprocess

def check_package(package_name):
    """Check if a package is installed and importable."""
    try:
        __import__(package_name)
        print(f"✅ {package_name} is installed and importable")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT installed or not importable")
        return False

def check_command(command):
    """Check if a command is available in the system."""
    try:
        result = subprocess.run([command, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ {command} is available: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {command} command failed")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print(f"❌ {command} command not found")
        return False

def main():
    print("🔍 Verifying build dependencies...")
    print(f"Python version: {sys.version}")
    print("-" * 50)
    
    # Check critical packages
    packages = [
        'django',
        'rest_framework',
        'gunicorn',
        'whitenoise',
        'reportlab',
        'weasyprint'
    ]
    
    all_good = True
    for package in packages:
        if not check_package(package):
            all_good = False
    
    print("-" * 50)
    
    # Check commands
    commands = ['gunicorn', 'python']
    for command in commands:
        if not check_command(command):
            all_good = False
    
    print("-" * 50)
    if all_good:
        print("🎉 All dependencies verified successfully!")
        sys.exit(0)
    else:
        print("💥 Some dependencies are missing!")
        sys.exit(1)

if __name__ == "__main__":
    main() 