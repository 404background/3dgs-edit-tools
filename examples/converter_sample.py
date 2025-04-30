#!/usr/bin/env python3
"""
3D Gaussian Splatting data conversion sample code

This sample performs the following operations:
1. Convert PLY format data to CSV
2. Edit CSV format data (adjust values)
3. Convert the edited CSV data back to PLY format

All output files are saved in the converted folder.
"""

import os
import sys
import csv
# Add path to import the library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the library
from src import convert_3dgs_to_csv, convert_csv_to_3dgs


def main():
    # Input file (PLY format)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_ply = os.path.join(current_dir, 'Haniwa.ply')
    
    # Check and create the converted directory
    converted_dir = os.path.join(current_dir, 'converted')
    if not os.path.exists(converted_dir):
        os.makedirs(converted_dir)
        print(f"Created 'converted' directory: {converted_dir}")
    
    print(f"Original PLY file: {input_ply}")
    
    # Convert PLY file to CSV
    csv_path = os.path.join(converted_dir, 'Haniwa.csv')
    footer_path = os.path.join(converted_dir, 'Haniwa_footer.tmp')
    csv_path, footer_path = convert_3dgs_to_csv(input_ply, csv_path, footer_path)
    print(f"Converted to CSV: {csv_path}")
    print(f"Saved footer: {footer_path}")
    
    # Load CSV file to check and edit content (optional)
    modified_csv_path = os.path.join(converted_dir, 'Haniwa_modified.csv')
    
    # Example of modifying CSV: scale coordinate values of the first 10 rows
    with open(csv_path, 'r') as csvfile, open(modified_csv_path, 'w', newline='') as outfile:
        reader = csv.reader(csvfile)
        writer = csv.writer(outfile)
        
        # Read and write the header row
        header = next(reader)
        writer.writerow(header)
        
        # Process data rows
        for i, row in enumerate(reader):
            if i < 10:  # Only modify the first 10 rows
                # Scale X, Y, Z coordinates (1.1x)
                # Note: Indices may vary depending on the data format
                row[0] = str(float(row[0]) * 1.1)  # X coordinate
                row[1] = str(float(row[1]) * 1.1)  # Y coordinate
                row[2] = str(float(row[2]) * 1.1)  # Z coordinate
            writer.writerow(row)
    
    print(f"Created modified CSV: {modified_csv_path}")
    
    # Convert modified CSV back to PLY
    output_ply = os.path.join(converted_dir, 'Haniwa_modified.ply')
    restored_ply = convert_csv_to_3dgs(modified_csv_path, footer_path, output_ply)
    print(f"Created modified PLY file: {restored_ply}")
    
    print("\nProcessing complete.")
    print(f"Original PLY file: {input_ply}")
    print(f"CSV file: {csv_path}")
    print(f"Modified CSV file: {modified_csv_path}")
    print(f"Modified PLY file: {restored_ply}")
    print(f"\nAll output files were saved in {converted_dir}")


if __name__ == "__main__":
    main()
