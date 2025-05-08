#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sample script demonstrating 3DGS file comparison features
"""

import os
import sys
from src.compare_gs import compare_3dgs_files, print_comparison_results

def main():
    """
    Example of using 3DGS comparison functionality
    """
    # Set up paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, "converted")
    os.makedirs(output_dir, exist_ok=True)
    
    # Example files to compare - we'll use existing PLY files in the examples directory
    file1 = os.path.join(current_dir, "Haniwa.ply")
    file2 = os.path.join(output_dir, "Haniwa_transformed.ply")
    
    # Check if files exist
    if not os.path.exists(file1) or not os.path.exists(file2):
        print(f"Error: One or both of the example files do not exist.")
        print(f"Make sure to run transform_sample.py first to generate the transformed model.")
        print(f"Missing files: {file1 if not os.path.exists(file1) else ''} "
              f"{file2 if not os.path.exists(file2) else ''}")
        return
    
    # Compare the files
    print(f"Comparing original and transformed models...")
    print(f"File 1: {file1}")
    print(f"File 2: {file2}")
    
    # Set output directory for comparison results
    comparison_dir = os.path.join(output_dir, "comparison_results")
    os.makedirs(comparison_dir, exist_ok=True)
    
    # Run comparison
    results = compare_3dgs_files(
        file1,
        file2,
        output_dir=comparison_dir,
        tolerance=1e-4,  # Adjust tolerance as needed
        visualize=True   # Generate visualization
    )
    
    # Print formatted results
    print_comparison_results(results, file1, file2)
    
    # Additional usage examples
    print("\n=== Advanced Usage Examples ===")
    
    # Example: Reading the difference CSV for further analysis
    if "diff_csv" in results and os.path.exists(results["diff_csv"]):
        print(f"\nDifference CSV file created at: {results['diff_csv']}")
        print("This file contains detailed information about all differences between the models.")
        print("You can load it in any CSV viewer or with pandas for further analysis.")
    
    # Example: Visualization file
    if "visualization" in results and os.path.exists(results["visualization"]):
        print(f"\nVisualization file created at: {results['visualization']}")
        print("This 3D visualization shows the points with differences, colored by difference magnitude.")
    
    print("\n=== How to Use in Your Code ===")
    print("Import and use the comparison function:")
    print("from src.compare_gs import compare_3dgs_files, print_comparison_results")
    print("results = compare_3dgs_files('file1.ply', 'file2.ply', output_dir='output', tolerance=1e-6)")
    print("# Access differences programmatically")
    print("if results.get('different_rows', 0) > 0:")
    print("    print(f\"Found {results['different_rows']} differences\")")

if __name__ == "__main__":
    main()
