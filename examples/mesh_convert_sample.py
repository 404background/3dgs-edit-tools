"""
Sample script demonstrating how to convert 3D Gaussian Splatting format to mesh.
This workflow allows for converting 3DGS data to a high-quality mesh with preserved colors,
minimal holes, and reduced surface roughness.

The script first converts 3DGS to point cloud format, then uses Open3D to generate the mesh.
"""

import os
import sys
import argparse

# Add the parent directory to the path to import the src package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import convert_3dgs_to_pointcloud
from src.pointcloud_to_mesh import convert_pointcloud_to_mesh


def main():
    """
    Demonstrates a workflow for converting 3DGS to mesh:
    1. Convert 3DGS to point cloud
    2. Convert point cloud to mesh with optimized settings for quality
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Convert 3D Gaussian Splatting to mesh format")
    parser.add_argument("--input_ply", default="Haniwa.ply", help="Input 3D Gaussian Splatting PLY file")
    parser.add_argument("--output_format", default="obj", choices=["obj", "ply", "stl"], 
                        help="Output mesh format (default: obj)")
    parser.add_argument("--method", default="hybrid", 
                        choices=["poisson", "ball_pivoting", "alpha_shape", "hybrid"],
                        help="Mesh reconstruction method (default: hybrid)")
    parser.add_argument("--quality", default="high", 
                        choices=["low", "normal", "high", "ultra"],
                        help="Reconstruction quality (default: high)")
    parser.add_argument("--smoothness", type=float, default=1.5,
                        help="Smoothness level (0.0-3.0, default: 1.5)")
    parser.add_argument("--fill_holes", action="store_true", 
                        help="Enable hole filling")
    parser.add_argument("--aggressive_holes", action="store_true", 
                        help="Use aggressive techniques for hole filling")
    parser.add_argument("--density", type=float, default=0.01,
                        help="Density threshold percentile for filtering (0.001-0.05, default: 0.01)")
    parser.add_argument("--neighbors", type=int, default=30,
                        help="Number of neighbors for normal estimation (10-100, default: 30)")
    parser.add_argument("--super_smooth", action="store_true",
                        help="Apply maximum smoothing (sets smoothness=3.0)")
    parser.add_argument("--depth", type=int, default=0,
                        help="Override default poisson depth (0=auto)")
    parser.add_argument("--scale", type=float, default=1.0,
                        help="Scale factor for the mesh (default: 1.0)")
    args = parser.parse_args()
    
    # Get current directory for correct path resolution
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)  # Parent directory of examples
    
    # Handle input file path - correcting path resolution
    if os.path.isabs(args.input_ply):
        # Absolute path
        input_3dgs_file = args.input_ply
    elif args.input_ply.startswith("examples/") or args.input_ply.startswith("examples\\"):
        # Path already has examples/ prefix, resolve against project root
        input_3dgs_file = os.path.join(project_root, args.input_ply)
    else:
        # Simple filename or relative path without examples/ prefix
        input_3dgs_file = os.path.join(current_dir, args.input_ply)
    
    # Verify the input file exists
    if not os.path.exists(input_3dgs_file):
        print(f"Error: Input file not found: {input_3dgs_file}")
        sys.exit(1)
        
    print(f"Using input file: {input_3dgs_file}")
    
    # Extract filename without extension for output file naming
    input_filename = os.path.basename(input_3dgs_file)
    input_base = os.path.splitext(input_filename)[0]
    
    # Make sure the converted directory exists
    converted_dir = os.path.join(current_dir, "converted")
    os.makedirs(converted_dir, exist_ok=True)
    
    # Apply super_smooth option if selected
    smoothness = args.smoothness
    if args.super_smooth:
        smoothness = 3.0
        print("Super smooth mode enabled (smoothness=3.0)")
    
    # Set default poisson depth based on quality if not specified
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
    
    # Define file paths with descriptive naming that includes parameters
    descriptive_name = f"{input_base}_{args.method}_{args.quality}"
    
    if args.method in ["poisson", "hybrid"]:
        descriptive_name += f"_d{poisson_depth}"
        
    descriptive_name += f"_smooth{smoothness:.1f}"
    
    if args.fill_holes:
        descriptive_name += "_holes" + ("_agg" if args.aggressive_holes else "")
        
    if args.density != 0.01:
        descriptive_name += f"_dt{args.density:.3f}"
        
    if args.neighbors != 30:
        descriptive_name += f"_nn{args.neighbors}"
    
    pointcloud_file = os.path.join(converted_dir, f"{input_base}_pointcloud.ply")
    mesh_file = os.path.join(converted_dir, f"{descriptive_name}.{args.output_format}")

    # STREAMLINED WORKFLOW
    print(f"\n=== 3D GAUSSIAN SPLATTING TO MESH CONVERSION WORKFLOW ===")
    print(f"Converting with parameters:")
    print(f" - Method: {args.method}")
    print(f" - Quality: {args.quality}")
    print(f" - Poisson depth: {poisson_depth}")
    print(f" - Smoothness: {smoothness}")
    print(f" - Fill holes: {'Enabled' + (' (Aggressive)' if args.aggressive_holes else '') if args.fill_holes else 'Disabled'}")
    print(f" - Density threshold: {args.density}")
    print(f" - Normal neighbors: {args.neighbors}")
    print(f" - Output format: {args.output_format}")
    print(f" - Scale factor: {args.scale}")
    print(f" - Output filename: {os.path.basename(mesh_file)}")
    
    # Step 1: Convert 3DGS to point cloud
    print(f"\n1. Converting 3D Gaussian Splatting to point cloud...")
    pointcloud_path = convert_3dgs_to_pointcloud(input_3dgs_file, pointcloud_file)
    print(f"   Point cloud saved to {pointcloud_path}")
    
    # Step 2: Convert point cloud to mesh with optimized settings
    print(f"\n2. Converting point cloud to mesh using {args.method} method with {args.quality} quality...")
    
    # Run the conversion with optimized settings for quality
    mesh_path = convert_pointcloud_to_mesh(
        pointcloud_path,
        mesh_file,
        output_format=args.output_format,
        poisson_depth=poisson_depth,
        method=args.method,
        quality=args.quality,
        smoothness=smoothness,
        fill_holes=args.fill_holes,
        aggressive_hole_filling=args.aggressive_holes,
        density_threshold_percentile=args.density,
        normal_neighbors=args.neighbors,
        write_vertex_colors=True,
        compute_normals=True,
        scale=args.scale
    )
    
    if mesh_path:
        print(f"\nMesh successfully created and saved to: {mesh_path}")
        print("\nRecommended next steps:")
        print("  - View the resulting mesh in your preferred 3D software")
        print("  - For OBJ files, check that the MTL file is present with the mesh")
        print("  - If the mesh has issues, try:")
        print("    * For more smoothness: increase --smoothness value or use --super_smooth")
        print("    * For fewer holes: use --fill_holes with --aggressive_holes")
        print("    * For better detail preservation: lower --density to 0.005")
        print("    * For smoother surfaces: increase --neighbors to 50 or 60")
    else:
        print("\nMesh conversion failed. Please check error messages above.")
    
    print("\nWorkflow complete!")


if __name__ == "__main__":
    main()
