#!/usr/bin/env python3
"""
3DGS Editor Package Build Tool

This script provides functionality for building and publishing the 3DGS Editor package.
It serves as a helper tool for publishing packages to PyPI.

Usage:
    python -m tools.build_package build - Build the package
    python -m tools.build_package publish - Publish the package to TestPyPI
    python -m tools.build_package publish-prod - Publish the package to production PyPI
"""

import argparse
import os
import sys
import shutil
from pathlib import Path
import subprocess

def check_requirements():
    """Check if required packages are installed"""
    try:
        import build
    except ImportError:
        print("Installing required packages for building...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "build", "twine"])

def clean_build_directories():
    """Clean up the build and dist directories"""
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    
    for pattern in dirs_to_clean:
        if '*' in pattern:
            # For patterns with wildcards
            for path in Path('.').glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
        else:
            # For explicit directories
            path = Path(pattern)
            if path.exists() and path.is_dir():
                shutil.rmtree(path)
    
    print("Cleanup completed: build/ and dist/ directories removed")

def build_package():
    """Build the package"""
    print("Building package...")
    
    # Build using build package
    subprocess.check_call([sys.executable, "-m", "build"])
    
    print("\nBuild successful! Output files created in dist directory")
    
    # Display created files
    print("\nBuild artifacts:")
    for file in Path("dist").glob("*"):
        print(f" - {file.name}")

def publish_to_testpypi():
    """Publish package to TestPyPI"""
    print("Publishing package to TestPyPI...")
    
    # Publish using twine
    subprocess.check_call([
        sys.executable, "-m", "twine", "upload", 
        "--repository", "testpypi", "dist/*"
    ])
    
    package_name = get_package_name()
    
    print(f"\nPublication successful! Package published to TestPyPI")
    print(f"\nInstallation instructions:")
    print(f"pip install --index-url https://test.pypi.org/simple/ {package_name}")

def publish_to_pypi():
    """Publish package to production PyPI"""
    print("Publishing package to production PyPI...")
    
    # Display confirmation message
    response = input("\nWarning: This will publish to production PyPI. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Operation cancelled")
        return
    
    # Publish using twine
    subprocess.check_call([
        sys.executable, "-m", "twine", "upload", "dist/*"
    ])
    
    package_name = get_package_name()
    
    print(f"\nPublication successful! Package published to production PyPI")
    print(f"\nInstallation instructions:")
    print(f"pip install {package_name}")

def get_package_name():
    """Get package name from pyproject.toml"""
    try:
        import tomli
        with open("pyproject.toml", "rb") as f:
            pyproject = tomli.load(f)
            return pyproject.get("project", {}).get("name", "3dgs-edit-tools")
    except:
        # In case tomli is not available or there's a reading error
        return "3dgs-edit-tools"

def main():
    parser = argparse.ArgumentParser(description='3DGS Editor Packaging Tool')
    
    subparsers = parser.add_subparsers(dest='command', help='commands')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean up build directories')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build package')
    
    # Publish command (TestPyPI)
    publish_parser = subparsers.add_parser('publish', help='Publish package to TestPyPI')
    
    # Publish command (production PyPI)
    publish_prod_parser = subparsers.add_parser('publish-prod', help='Publish package to production PyPI')
    
    args = parser.parse_args()
    
    # Check required packages
    check_requirements()
    
    # Execute command
    if args.command == 'clean':
        clean_build_directories()
    elif args.command == 'build':
        clean_build_directories()
        build_package()
    elif args.command == 'publish':
        # Check if attempting to publish without building
        if not Path('dist').exists() or not any(Path('dist').glob('*')):
            print("No artifacts found in dist directory. Build first? (y/N): ", end='')
            if input().lower() == 'y':
                clean_build_directories()
                build_package()
            else:
                print("Skipping build")
        
        publish_to_testpypi()
    elif args.command == 'publish-prod':
        # Check if attempting to publish without building
        if not Path('dist').exists() or not any(Path('dist').glob('*')):
            print("No artifacts found in dist directory. Build first? (y/N): ", end='')
            if input().lower() == 'y':
                clean_build_directories()
                build_package()
            else:
                print("Skipping build")
        
        publish_to_pypi()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()