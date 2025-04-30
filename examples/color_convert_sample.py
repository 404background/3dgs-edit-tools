#!/usr/bin/env python3
"""
Simple script to change Haniwa.ply colors to black

Created based on haniwa_sample.py with minimal changes to only modify colors to black.
All generated files will be saved in the 'converted' folder.
"""

import os
import sys
import csv

# Add the source code directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the library
from src import convert_3dgs_to_csv, convert_csv_to_3dgs


def main():
    # Sample file path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_ply = os.path.join(current_dir, 'Haniwa.ply')
    
    # Check and create the converted directory
    converted_dir = os.path.join(current_dir, 'converted')
    if not os.path.exists(converted_dir):
        os.makedirs(converted_dir)
        print(f"Created 'converted' directory: {converted_dir}")
    
    print(f"Processing Haniwa.ply: {input_ply}")
    
    # Convert PLY file to CSV
    csv_path = os.path.join(converted_dir, 'Haniwa.csv')
    footer_path = os.path.join(converted_dir, 'Haniwa_footer.tmp')
    csv_path, footer_path = convert_3dgs_to_csv(input_ply, csv_path, footer_path)
    print(f"Converted to CSV: {csv_path}")
    print(f"Saved footer data: {footer_path}")
    
    # Read the CSV file
    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        data = [row for row in reader]
    
    # Find color-related attribute indices
    color_indices = []
    for i, attr in enumerate(header):
        if attr.startswith('f_dc_'):
            color_indices.append(i)
    
    if color_indices:
        print(f"Found color-related attributes: {[header[i] for i in color_indices]}")
    else:
        print("No color-related attributes found.")
        return
    
    # Set the path for the modified file
    modified_csv_path = os.path.join(converted_dir, 'Haniwa_black.csv')
    
    # Modify CSV data (change colors to black)
    print("\n=== Editing data ===")
    print("- Changing all colors to black...")
    
    with open(modified_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        
        for row in data:
            # Change all color values to black
            for i in color_indices:
                row[i] = "-1.0"  # Black color (value adjusted based on original sample)
            
            writer.writerow(row)
    
    print(f"Saved modified CSV: {modified_csv_path}")
    
    # Convert edited CSV back to PLY
    output_ply = os.path.join(converted_dir, 'Haniwa_black.ply')
    restored_ply = convert_csv_to_3dgs(modified_csv_path, footer_path, output_ply)
    print(f"\nConverted modified data to PLY: {restored_ply}")
    
    print("\n=== Conversion summary ===")
    print(f"Original PLY file: {input_ply}")
    print(f"Intermediate CSV file: {csv_path}")
    print(f"Blackened CSV file: {modified_csv_path}")
    print(f"Final PLY file: {restored_ply}")
    print(f"\nAll output files were saved in {converted_dir}")
    print("\nPlease compare the original PLY file with the blackened PLY file.")


if __name__ == "__main__":
    main()
