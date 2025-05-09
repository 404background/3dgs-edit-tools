#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
3D Gaussian Splatting to Mesh Converter
---------------------------------------
Converts 3D Gaussian Splatting (3DGS) format directly to mesh formats
like OBJ, PLY, and STL with various surface reconstruction options.

This module serves as a direct conversion pipeline, internally using
the point cloud conversion and mesh reconstruction capabilities.
"""

import os
import argparse
import sys
from pathlib import Path
from .gs_to_pointcloud import convert_3dgs_to_pointcloud
from .pointcloud_to_mesh import convert_pointcloud_to_mesh

def convert_3dgs_to_mesh(
    input_file,
    output_file=None,
    output_format="obj",
    poisson_depth=9,
    scale=1.0,
    orientation_fix=True,
    compute_normals=True,
    write_vertex_colors=True,
    method="poisson",
    quality="normal",
    save_to_converted=True,
    fill_holes=False,
    smoothness=1.0,
    aggressive_hole_filling=False,
    density_threshold_percentile=0.01,
    normal_neighbors=30
):
    """
    Convert 3D Gaussian Splatting format directly to mesh
    This is a convenience wrapper that first converts 3DGS to point cloud,
    then converts the point cloud to mesh.
    
    Parameters:
    -----------
    input_file : str
        Path to the input 3DGS PLY file
    output_file : str, optional
        Path to the output mesh file. If None, it will be created based on input_file
    output_format : str, optional
        Output file format: 'ply', 'stl', 'obj', etc. (Default is 'obj')
    poisson_depth : int, optional
        Depth parameter for Poisson reconstruction. Higher values create more detailed meshes
        but require more computation. Default is 9.
    scale : float, optional
        Scale factor to apply to the mesh. Default is 1.0.
    orientation_fix : bool, optional
        If True, applies orientation correction for OBJ format. Default is True.
    compute_normals : bool, optional
        If True, computes normals for the point cloud before reconstruction. Default is True.
    write_vertex_colors : bool, optional
        If True, preserves vertex colors in formats that support it. Default is True.
    method : str, optional
        Reconstruction method: 'poisson', 'ball_pivoting', 'alpha_shape', or 'hybrid'. Default is 'poisson'.
    quality : str, optional
        Quality preset: 'low', 'normal', 'high', or 'ultra'. Default is 'normal'.
    save_to_converted : bool, optional
        If True, saves output files to a 'converted' subfolder. Default is True.
    fill_holes : bool, optional
        If True, attempt to fill holes in the mesh. Default is False.
    smoothness : float, optional
        Controls the strength of the smoothing. Values range from 0.0 to 2.0. Default is 1.0.
    aggressive_hole_filling : bool, optional
        If True, use more aggressive techniques to fill holes. Default is False.
    density_threshold_percentile : float, optional
        Percentile threshold for density filtering (0.0-1.0). Lower values preserve more points.
    normal_neighbors : int, optional
        Number of neighbors to use for normal estimation. Higher values create smoother normals.
        
    Returns:
    --------
    str
        Path to the output mesh file
    """
    # Generate a temporary filename for the intermediate point cloud
    input_path = Path(input_file)
    temp_dir = input_path.parent
    if save_to_converted:
        # Create 'converted' subfolder if it doesn't exist
        converted_dir = temp_dir / 'converted'
        converted_dir.mkdir(exist_ok=True)
        temp_dir = converted_dir
    
    temp_pointcloud = temp_dir / f"{input_path.stem}_pointcloud.ply"
    
    print(f"Step 1: Converting 3DGS to point cloud format...")
    # Convert 3DGS to point cloud
    pointcloud_file = convert_3dgs_to_pointcloud(input_file, str(temp_pointcloud))
    
    if not pointcloud_file or not os.path.exists(pointcloud_file):
        print(f"Error: Failed to create point cloud from 3DGS file")
        return None
    
    print(f"Step 2: Converting point cloud to mesh...")
    # Convert point cloud to mesh
    mesh_file = convert_pointcloud_to_mesh(
        pointcloud_file,
        output_file,
        output_format,
        poisson_depth,
        scale,
        orientation_fix,
        compute_normals,
        write_vertex_colors,
        method,
        quality,
        save_to_converted,
        fill_holes,
        smoothness,
        aggressive_hole_filling,
        density_threshold_percentile,
        normal_neighbors
    )
    
    return mesh_file

def main():
    """
    Command-line entry point for 3DGS to mesh conversion.
    Parses arguments and calls the convert_3dgs_to_mesh function.
    """
    parser = argparse.ArgumentParser(description='Convert 3D Gaussian Splatting format to mesh')
    parser.add_argument('input_file', help='Input 3DGS file (.ply)')
    parser.add_argument('--output', '-o', help='Output mesh file')
    parser.add_argument('--format', '-f', default='obj', help='Output format: obj (default), ply, stl')
    parser.add_argument('--method', '-m', default='hybrid', 
                       choices=['poisson', 'ball_pivoting', 'alpha_shape', 'hybrid'],
                       help='Surface reconstruction method')
    parser.add_argument('--depth', '-d', type=int, default=0, 
                       help='Depth for Poisson reconstruction (0=auto based on quality)')
    parser.add_argument('--quality', '-q', default='high',
                       choices=['low', 'normal', 'high', 'ultra'],
                       help='Quality preset')
    parser.add_argument('--scale', '-s', type=float, default=1.0,
                       help='Scale factor for the mesh')
    parser.add_argument('--no-orientation-fix', action='store_false', dest='orientation_fix',
                       help='Disable orientation fix for OBJ files')
    parser.add_argument('--no-colors', action='store_false', dest='colors',
                       help='Disable vertex color preservation')
    parser.add_argument('--no-normals', action='store_false', dest='normals',
                       help='Disable normal computation')
    parser.add_argument('--no-converted-folder', action='store_false', dest='save_to_converted',
                       help='Save output to same folder as input instead of "converted" subfolder')
    parser.add_argument('--fill-holes', action='store_true',
                       help='Enable conservative hole filling')
    parser.add_argument('--smoothness', type=float, default=1.5,
                       help='Smoothness factor (0.0-3.0, default: 1.5)')
    parser.add_argument('--super-smooth', action='store_true',
                       help='Apply enhanced smoothing (sets smoothness to 3.0)')
    parser.add_argument('--aggressive-holes', action='store_true',
                       help='Use aggressive techniques for hole filling')
    parser.add_argument('--density', '--density-threshold-percentile', type=float, default=0.01,
                       help='Percentile threshold for density filtering (default: 0.01, lower values preserve more points)')
    parser.add_argument('--neighbors', '--normal-neighbors', type=int, default=30,
                       help='Number of neighbors for normal estimation (default: 30, higher values give smoother normals)')
    
    args = parser.parse_args()
    
    # Apply super-smooth option if selected
    smoothness = 3.0 if args.super_smooth else args.smoothness
    
    # Calculate poisson depth based on quality if not specified
    poisson_depth = args.depth
    if poisson_depth == 0:
        if args.quality == "low":
            poisson_depth = 7
        elif args.quality == "normal":
            poisson_depth = 9
        elif args.quality == "high":
            poisson_depth = 10
        else:  # ultra
            poisson_depth = 11

    # Convert mesh
    output_path = convert_3dgs_to_mesh(
        args.input_file,
        args.output,
        args.format,
        poisson_depth,
        args.scale,
        args.orientation_fix,
        args.normals,
        args.colors,
        args.method,
        args.quality,
        args.save_to_converted,
        args.fill_holes,
        smoothness,
        args.aggressive_holes,
        args.density,
        args.neighbors
    )
    
    if output_path:
        print(f"\nMesh successfully created and saved to: {output_path}")
        print("\nRecommended next steps:")
        print("  - View the resulting mesh in your preferred 3D software")
        print("  - For OBJ files, check that the MTL file is present with the mesh")
        print("  - If the mesh has issues, try adjusting parameters like smoothness, density, or neighbors")
    else:
        print("Conversion failed")
        sys.exit(1)

def main_3dgs_to_mesh():
    """Entry point for the 3dgs-to-mesh script"""
    main()

if __name__ == "__main__":
    main()
