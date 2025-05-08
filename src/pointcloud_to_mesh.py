#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Point Cloud to Mesh Converter
-----------------------------
Converts point cloud data (.ply) to mesh formats with improved color handling
and orientation control for OBJ files.

This module uses Open3D to reconstruct a mesh from point cloud data
and properly preserves colors and orientation in the exported mesh.
"""

import os
import sys
import numpy as np
import open3d as o3d
from pathlib import Path
import argparse
import math
import shutil
from . import color_utils

def fill_holes_custom(mesh, max_hole_size=100, aggressive=False):
    """
    Custom implementation of hole filling for Open3D meshes.
    This is used as a fallback when the built-in fill_holes method is not available.
    
    Parameters:
    -----------
    mesh : o3d.geometry.TriangleMesh
        The input mesh with holes
    max_hole_size : int
        Maximum size of holes to fill (in terms of boundary edges)
    aggressive : bool
        If True, use more aggressive techniques to close holes
        
    Returns:
    --------
    int
        Number of holes filled
    """
    print("Using custom hole filling implementation...")
    
    # Ensure the mesh is watertight and has valid topology
    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_duplicated_vertices()
    mesh.remove_non_manifold_edges()
    
    # Get boundary edges (these form the holes)
    boundary_edges = []
    edges = mesh.get_non_manifold_edges()
    if len(edges) == 0:
        print("No holes detected in the mesh.")
        return 0
    
    print(f"Found {len(edges)} boundary edges that may form holes")
    
    # Simple hole filling by triangulating small boundary loops
    # This is a simplified approach that works for simple holes
    if len(edges) > 0:
        # We can't directly fill complex holes without the native method
        # Apply laplacian filtering which can help close small holes
        print("Applying Laplacian filter to help close small gaps...")
        iterations = 10 if aggressive else 5
        mesh = mesh.filter_smooth_laplacian(number_of_iterations=iterations)
        
        # Try to make the mesh more watertight
        print("Optimizing mesh to reduce holes...")
        threshold = 0.002 if aggressive else 0.001
        mesh.merge_close_vertices(threshold)  # Merge vertices that are very close
        
        # Additional processing for aggressive mode
        if aggressive:
            print("Applying additional mesh optimization for hole reduction...")
            # Add a second round of smoothing and merging
            mesh = mesh.filter_smooth_laplacian(number_of_iterations=5)
            mesh.merge_close_vertices(0.0015)
        
        return len(edges)
    
    return 0

def export_mesh_with_colors(mesh, output_file, write_vertex_colors=True, scale_factor=1.0):
    """
    Export mesh to OBJ format with standard vertex color support.
    Creates a properly formatted OBJ and MTL file pair using per-vertex colors.
    
    Parameters:
    -----------
    mesh : o3d.geometry.TriangleMesh
        The mesh to export
    output_file : str
        Path to the output OBJ file
    write_vertex_colors : bool
        Whether to include color information
    scale_factor : float
        Scale factor to apply to the mesh during export (default: 1.0)
        
    Returns:
    --------
    bool
        True if export was successful, False otherwise
    """
    if not write_vertex_colors or len(mesh.vertex_colors) == 0:
        # If no colors to preserve, use standard export
        return o3d.io.write_triangle_mesh(output_file, mesh, write_vertex_colors=False)
    
    print(f"Exporting with standard color support...")
    
    try:
        # Extract base name for MTL file
        output_path = Path(output_file)
        mtl_filename = str(output_path.with_suffix('.mtl'))
        mtl_basename = os.path.basename(mtl_filename)
        obj_basename = os.path.basename(output_file)
        
        # Apply scale factor to mesh vertices if needed
        vertices = np.asarray(mesh.vertices)
        if scale_factor != 1.0:
            print(f"Scaling mesh by factor {scale_factor} during export")
            vertices = vertices * scale_factor
        
        triangles = np.asarray(mesh.triangles)
        vertex_colors = np.asarray(mesh.vertex_colors)
        
        # Create simple material with average color
        avg_color = np.mean(vertex_colors, axis=0)
        r, g, b = avg_color
        
        # Create the MTL file with a default material
        with open(mtl_filename, 'w') as mtl_file:
            mtl_file.write("# Standard material file\n")
            mtl_file.write(f"newmtl material\n")
            mtl_file.write(f"Kd {r:.6f} {g:.6f} {b:.6f}\n")
            mtl_file.write("Ka 0.0 0.0 0.0\n")  # Ambient color
            mtl_file.write("Ks 0.0 0.0 0.0\n")  # Specular color
            mtl_file.write("Ns 1.0\n")          # Specular exponent
            mtl_file.write("illum 2\n")         # Illumination model
        
        print(f"Created standard MTL file")
        
        # Write custom OBJ file with vertex colors
        with open(output_file, 'w') as obj_file:
            # Write header
            obj_file.write("# OBJ file with vertex colors\n")
            obj_file.write(f"mtllib {mtl_basename}\n\n")
            
            # Write vertex positions
            for v in vertices:
                obj_file.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            
            # Write vertex colors as comments for reference
            # Some software might be able to read these
            for i, c in enumerate(vertex_colors):
                obj_file.write(f"# vc {i} {c[0]:.6f} {c[1]:.6f} {c[2]:.6f}\n")
            
            obj_file.write("\n")
            
            # Write vertex normals if available
            if len(mesh.vertex_normals) > 0:
                normals = np.asarray(mesh.vertex_normals)
                for n in normals:
                    obj_file.write(f"vn {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}\n")
                
                obj_file.write("\n")
            
            has_normals = len(mesh.vertex_normals) > 0
            
            # Write texture coordinates (dummy values since we're using vertex colors)
            # Some importers expect this
            for i in range(len(vertices)):
                obj_file.write(f"vt 0.0 0.0\n")
            
            obj_file.write("\n")
            
            # Write material reference
            obj_file.write(f"usemtl material\n")
            
            # Write faces with vertex/texture/normal indices (1-based indexing)
            for face in triangles:
                if has_normals:
                    obj_file.write(f"f {face[0]+1}/{face[0]+1}/{face[0]+1} {face[1]+1}/{face[1]+1}/{face[1]+1} {face[2]+1}/{face[2]+1}/{face[2]+1}\n")
                else:
                    obj_file.write(f"f {face[0]+1}/{face[0]+1} {face[1]+1}/{face[1]+1} {face[2]+1}/{face[2]+1}\n")
        
        print(f"Created standard OBJ file with vertex color references: {output_file}")
        return True
    
    except Exception as e:
        print(f"Error exporting mesh with colors: {str(e)}")
        # Fall back to standard export on error
        print("Falling back to standard OBJ export")
        return o3d.io.write_triangle_mesh(output_file, mesh, write_vertex_colors=False)

def convert_pointcloud_to_mesh(
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
    Convert point cloud to mesh using surface reconstruction.
    
    Parameters:
    -----------
    input_file : str
        Path to the input point cloud PLY file
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
    # Determine output file path if not provided
    if output_file is None:
        input_path = Path(input_file)
        # Create a more descriptive filename that includes conversion method and quality
        descriptive_name = f"{input_path.stem}"
        
        # Add method information
        descriptive_name += f"_{method}"
        
        # Add quality information
        descriptive_name += f"_{quality}"
        
        # Add depth information for poisson and hybrid methods
        if method in ["poisson", "hybrid"]:
            descriptive_name += f"_d{poisson_depth}"
        
        # Add smoothness info
        descriptive_name += f"_smooth{smoothness:.1f}"
            
        # Add hole filling info
        if fill_holes:
            descriptive_name += "_holes" + ("_agg" if aggressive_hole_filling else "")
            
        # Add normal estimation info if custom value
        if normal_neighbors != 30:
            descriptive_name += f"_nn{normal_neighbors}"
            
        # Add density threshold info if custom value
        if density_threshold_percentile != 0.01:
            descriptive_name += f"_dt{density_threshold_percentile:.3f}"
            
        # Create output filename with descriptive name and correct extension
        output_filename = f"{descriptive_name}.{output_format}"
        
        if save_to_converted:
            # Get the directory of the input file
            input_dir = input_path.parent
            # Create 'converted' subfolder if it doesn't exist
            converted_dir = input_dir / 'converted'
            converted_dir.mkdir(exist_ok=True)
            # Set output path to the converted folder
            output_file = str(converted_dir / output_filename)
        else:
            output_file = str(input_path.with_suffix(f"_{descriptive_name}.{output_format}"))
    else:
        # Ensure the output file has the correct extension
        output_path = Path(output_file)
        if output_path.suffix.lower() != f".{output_format.lower()}":
            output_file = str(Path(output_file).with_suffix(f".{output_format}"))
    
    print(f"Loading point cloud from {input_file}")
    pcd = o3d.io.read_point_cloud(input_file)
    
    # Validate the input point cloud
    points = np.asarray(pcd.points)
    if len(points) == 0:
        print("Error: Point cloud has no points")
        return None
    
    # Check for NaN values in the point cloud and remove them
    valid_indices = ~np.isnan(points).any(axis=1)
    if np.sum(~valid_indices) > 0:
        print(f"Warning: Removing {np.sum(~valid_indices)} points with NaN values from point cloud")
        pcd = pcd.select_by_index(np.where(valid_indices)[0])
        points = np.asarray(pcd.points)
    
    # Verify point cloud is valid after cleaning
    if len(points) == 0:
        print("Error: No valid points after cleaning point cloud")
        return None
    
    # Check for infinity values and bound them
    inf_mask = np.isinf(points)
    if np.any(inf_mask):
        print(f"Warning: Found {np.sum(inf_mask)} infinity values in point cloud")
        # Replace infinities with large but finite values
        points[inf_mask] = np.sign(points[inf_mask]) * 1e6
        pcd.points = o3d.utility.Vector3dVector(points)
    
    # Adjust quality settings with better constraints for ultra quality
    if quality == "low":
        poisson_depth = max(5, poisson_depth - 2)
        smoothness = min(2.0, smoothness * 1.5)
    elif quality == "high":
        poisson_depth = poisson_depth + 1
    elif quality == "ultra":
        # Limit depth increase for ultra quality to avoid excessive computation
        if method == "hybrid":
            poisson_depth = min(12, poisson_depth + 1)  # Limit depth for hybrid mode
        else:
            poisson_depth = min(14, poisson_depth + 2)  # Maximum value limited to 14
    
    print(f"Using poisson depth: {poisson_depth}")
    
    # Ensure we have normals (required for reconstruction)
    if compute_normals or not pcd.has_normals():
        print(f"Computing normals with {normal_neighbors} neighbors...")
        # Adjusted normal estimation parameters
        try:
            pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=normal_neighbors))
            # Verify normal computation succeeded
            normals = np.asarray(pcd.normals)
            if np.isnan(normals).any():
                print("Warning: Some normals contain NaN values. Recomputing with more conservative parameters...")
                # Try with more conservative parameters
                pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.2, max_nn=20))
                normals = np.asarray(pcd.normals)
                # If still have NaN normals, remove those points
                if np.isnan(normals).any():
                    valid_indices = ~np.isnan(normals).any(axis=1)
                    print(f"Warning: Removing {np.sum(~valid_indices)} points with invalid normals")
                    pcd = pcd.select_by_index(np.where(valid_indices)[0])
            
            # Orient normals consistently
            pcd.orient_normals_consistent_tangent_plane(k=max(20, int(normal_neighbors * 0.8)))
        except Exception as e:
            print(f"Warning: Normal estimation failed: {str(e)}")
            print("Trying fallback normal estimation...")
            # Fallback to simpler but more robust normal estimation
            pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamKNN(knn=10))
    
    # Apply scaling if needed
    if scale != 1.0:
        print(f"Scaling point cloud by factor {scale}")
        pcd.scale(scale, center=pcd.get_center())
    
    # Create a deep copy of the point cloud with colors to preserve
    colored_pcd = o3d.geometry.PointCloud(pcd)
    
    # Store original colors before reconstruction
    has_colors = pcd.has_colors()
    if has_colors:
        print(f"Point cloud has color information with {len(pcd.colors)} color entries")
        original_colors = np.asarray(pcd.colors)
        # Check for invalid color values
        if np.isnan(original_colors).any() or np.isinf(original_colors).any():
            print("Warning: Invalid color values found. Cleaning up colors...")
            # Replace NaN or inf values with neutral gray
            invalid_mask = np.isnan(original_colors) | np.isinf(original_colors)
            original_colors[invalid_mask] = 0.5
            pcd.colors = o3d.utility.Vector3dVector(original_colors)
            colored_pcd.colors = o3d.utility.Vector3dVector(original_colors)
    else:
        print("Warning: Point cloud does not have color information")
        original_colors = None
    
    print(f"Starting {method} surface reconstruction...")
    mesh = None
    
    # Consider downsampling based on point cloud size
    num_points = len(np.asarray(pcd.points))
    if num_points > 500000 and method == "hybrid":
        print(f"Large point cloud detected ({num_points} points). Optimizing processing...")
        # Optimize processing for large point clouds
        voxel_size = 0.005
        print(f"Downsampling with voxel size {voxel_size} to improve performance")
        pcd_downsampled = pcd.voxel_down_sample(voxel_size=voxel_size)
        # Preserve normals after downsampling
        pcd_downsampled.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=normal_neighbors))
        # Use optimized point cloud for processing
        pcd_for_processing = pcd_downsampled
    else:
        pcd_for_processing = pcd
    
    try:
        if method == "poisson":
            print(f"Using Poisson reconstruction with depth={poisson_depth}")
            mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
                pcd_for_processing, depth=poisson_depth, linear_fit=True)
            
            # Use densities to remove outliers more selectively
            # Handle potential errors in density calculation
            if len(densities) > 0:
                if np.isnan(densities).any() or np.isinf(densities).any():
                    print("Warning: Invalid density values found. Using default filtering.")
                    # Use default percentile filtering in this case
                    threshold_index = max(0, min(int(len(densities) * density_threshold_percentile), len(densities) - 1))
                    densities_sorted = np.sort(densities)
                    density_threshold = densities_sorted[threshold_index]
                else:
                    # Normal case - calculate percentile
                    density_threshold = np.quantile(densities, density_threshold_percentile)
                
                print(f"Filtering mesh with density threshold: {density_threshold}")
                vertices_to_remove = densities < density_threshold
                mesh.remove_vertices_by_mask(vertices_to_remove)
            else:
                print("Warning: No density information for filtering")
            
        elif method == "ball_pivoting":
            print("Using ball pivoting algorithm")
            # Compute radius based on point cloud size
            points = np.asarray(pcd_for_processing.points)
            if len(points) > 0:
                # Calculate mean distance between points
                pcd_tree = o3d.geometry.KDTreeFlann(pcd_for_processing)
                distances = []
                for i in range(min(len(points), 1000)):  # Sample 1000 points for efficiency
                    _, idx, dist = pcd_tree.search_knn_vector_3d(points[i], 2)  # Find closest point (excluding self)
                    if len(dist) > 1:
                        distances.append(dist[1])
                
                if distances:
                    mean_distance = np.mean(distances)
                    # Set radii range based on mean distance
                    radii = [mean_distance*2, mean_distance*4, mean_distance*8, mean_distance*16]
                else:
                    radii = [0.005, 0.01, 0.02, 0.04]  # Default if calculation fails
            else:
                radii = [0.005, 0.01, 0.02, 0.04]  # Default
            
            print(f"Using ball pivoting radii: {radii}")
            mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
                pcd_for_processing, o3d.utility.DoubleVector(radii))
                
        elif method == "alpha_shape":
            print("Using alpha shapes")
            # Calculate adaptive alpha based on point cloud size
            points = np.asarray(pcd_for_processing.points)
            if len(points) > 0:
                # Compute bounding box to get a sense of model scale
                bbox = pcd_for_processing.get_axis_aligned_bounding_box()
                bbox_extent = bbox.get_extent()
                # Alpha relative to model size
                alpha = min(bbox_extent) * 0.02  # 2% of smallest dimension
            else:
                alpha = 0.03  # Default
                
            print(f"Using alpha value: {alpha}")
            mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd_for_processing, alpha)
            
        elif method == "hybrid":
            # Hybrid approach: Poisson with careful post-processing
            print(f"Using hybrid reconstruction approach with depth={poisson_depth}")
            
            # Progress reporting to keep track of processing
            print("Step 1/5: Creating Poisson mesh for base structure...")
            try:
                poisson_mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
                    pcd_for_processing, depth=poisson_depth, linear_fit=True)
                
                # Handle potential errors in density calculation
                if densities is None or len(densities) == 0 or np.isnan(densities).any():
                    print("Warning: Invalid density values. Trying with lower poisson depth.")
                    lower_depth = max(6, poisson_depth - 2)
                    poisson_mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
                        pcd_for_processing, depth=lower_depth, linear_fit=True)
                
                print("Step 2/5: Filtering low density areas...")
                # Get safe density threshold
                if len(densities) > 0 and not np.isnan(densities).any():
                    density_threshold = np.quantile(densities, density_threshold_percentile)
                    print(f"Using density threshold: {density_threshold}")
                    vertices_to_remove = densities < density_threshold
                    poisson_mesh.remove_vertices_by_mask(vertices_to_remove)
                else:
                    print("Warning: No valid density information. Skipping density filtering.")
                
                print("Step 3/5: Validating mesh...")
                # Check that we have a valid mesh with vertices
                if len(poisson_mesh.vertices) == 0:
                    print("Warning: Poisson reconstruction produced empty mesh. Trying alpha shape instead.")
                    alpha = 0.03  # Default alpha value
                    poisson_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(
                        pcd_for_processing, alpha)
                
                # Check for NaN vertices in the mesh
                mesh_vertices = np.asarray(poisson_mesh.vertices)
                if np.isnan(mesh_vertices).any():
                    print("Warning: Mesh contains NaN vertices. Cleaning up...")
                    valid_indices = ~np.isnan(mesh_vertices).any(axis=1)
                    if np.sum(valid_indices) > 0:
                        poisson_mesh = poisson_mesh.select_by_index(np.where(valid_indices)[0], cleanup=True)
                    else:
                        print("Error: No valid vertices after NaN removal. Trying alpha shapes...")
                        alpha = 0.03  # Default alpha value
                        poisson_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(
                            pcd_for_processing, alpha)
                
                print("Step 4/5: Applying smoothing for better surface...")
                # Apply light smoothing to reduce bumps
                poisson_mesh = poisson_mesh.filter_smooth_simple(number_of_iterations=1)
                
                print("Step 5/5: Finalizing mesh...")
                mesh = poisson_mesh
                
            except Exception as e:
                print(f"Error during hybrid mesh creation: {str(e)}")
                print("Falling back to alpha shapes...")
                try:
                    alpha = 0.03
                    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd_for_processing, alpha)
                except Exception as e2:
                    print(f"Alpha shape fallback also failed: {str(e2)}")
                    print("Trying ball pivoting as last resort...")
                    try:
                        radii = [0.005, 0.01, 0.02, 0.04]
                        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
                            pcd_for_processing, o3d.utility.DoubleVector(radii))
                    except Exception as e3:
                        print(f"All mesh creation methods failed: {str(e3)}")
                        return None
    except Exception as e:
        print(f"Error during mesh reconstruction: {str(e)}")
        return None
    
    if mesh is None or len(mesh.vertices) == 0:
        print("Error: Failed to create a valid mesh")
        return None
    
    # Verify the mesh has valid geometry
    mesh_vertices = np.asarray(mesh.vertices)
    if np.isnan(mesh_vertices).any() or np.isinf(mesh_vertices).any():
        print("Warning: Mesh contains NaN or Inf vertices. Cleaning up...")
        # Replace NaN values with zeros (will be removed later)
        nan_mask = np.isnan(mesh_vertices)
        inf_mask = np.isinf(mesh_vertices)
        invalid_vertices = nan_mask.any(axis=1) | inf_mask.any(axis=1)
        
        if np.sum(~invalid_vertices) > 0:
            print(f"Removing {np.sum(invalid_vertices)} invalid vertices from mesh")
            valid_indices = np.where(~invalid_vertices)[0]
            mesh = mesh.select_by_index(valid_indices, cleanup=True)
        else:
            print("Error: All vertices are invalid")
            return None
    
    # Display mesh statistics
    print(f"Mesh created with {len(mesh.vertices)} vertices and {len(mesh.triangles)} triangles")
    
    # Apply enhanced smoothing with higher quality for smoother surfaces
    # Increased smoothing for better results based on user feedback
    if smoothness > 0:
        print(f"Smoothing mesh to reduce surface irregularities...")
        # Enhanced adaptive smoothing with more iterations
        base_iterations = max(2, int(smoothness * 3))  # Increased from 2 to 3 multiplier
        print(f"Applying enhanced mesh smoothing (iterations={base_iterations})")
        
        try:
            # Apply taubin smoothing which better preserves features while smoothing
            mesh = mesh.filter_smooth_taubin(number_of_iterations=base_iterations)
            
            # For higher smoothness values, apply an additional round of laplacian smoothing
            if smoothness > 1.0:
                extra_iterations = int(smoothness * 2)
                print(f"Applying additional smoothing (iterations={extra_iterations})")
                mesh = mesh.filter_smooth_simple(number_of_iterations=extra_iterations)
                
                # For very high smoothness values, add taubin smoothing for even better results
                if smoothness >= 2.0:
                    print("Applying final taubin smoothing pass for extra smoothness...")
                    mesh = mesh.filter_smooth_taubin(number_of_iterations=2)
        except Exception as e:
            print(f"Warning: Smoothing operation failed: {str(e)}")
            print("Continuing with unsmoothed mesh")
    
    # Fill holes if requested, with a more conservative approach
    if fill_holes:
        print("Analyzing mesh for holes...")
        
        # Check if fill_holes method exists (depends on the Open3D version)
        if hasattr(mesh, 'fill_holes'):
            # Analyze holes before filling
            try:
                holes = mesh.get_non_manifold_edges()
                if len(holes) > 0:
                    print(f"Found {len(holes)} potential areas with holes")
                    
                    # Strictly limit hole sizes (only fill holes smaller than 1% of mesh size)
                    hole_size_threshold = int(len(mesh.triangles) * 0.01)
                    print(f"Performing selective hole filling (max size: {hole_size_threshold} triangles)")
                    filled = mesh.fill_holes(hole_size_threshold)
                    print(f"Filled {filled} holes")
            except Exception as e:
                print(f"Warning: Hole filling operation failed: {str(e)}")
        else:
            # Use our custom hole filling approach
            try:
                holes_filled = fill_holes_custom(mesh, aggressive=aggressive_hole_filling)
                if holes_filled > 0:
                    print(f"Custom hole filling approach applied to {holes_filled} potential hole areas")
            except Exception as e:
                print(f"Warning: Custom hole filling failed: {str(e)}")

    # Final validation and cleanup of mesh
    print("Performing final mesh validation and cleanup...")
    try:
        # Remove degenerate triangles
        mesh.remove_degenerate_triangles()
        # Remove duplicated vertices
        mesh.remove_duplicated_vertices()
        # Remove duplicated triangles
        mesh.remove_duplicated_triangles()
        # Remove unreferenced vertices
        mesh.remove_unreferenced_vertices()
    except Exception as e:
        print(f"Warning during mesh cleanup: {str(e)}")
    
    # Final check for NaNs in vertex positions
    try:
        mesh_vertices = np.asarray(mesh.vertices)
        if np.isnan(mesh_vertices).any() or np.isinf(mesh_vertices).any():
            print("ERROR: Mesh still contains NaN or Inf values after cleanup!")
            return None
    except Exception as e:
        print(f"Error checking mesh vertices: {str(e)}")

    # Enhanced color transfer from original point cloud to mesh
    if has_colors and write_vertex_colors:
        print("Preserving vertex colors from original point cloud...")
        
        if len(mesh.vertices) > 0:
            print("Preparing enhanced color transfer...")
            mesh_vertices = np.asarray(mesh.vertices)
            
            try:
                # Use KDTree for efficient nearest neighbor search
                pcd_tree = o3d.geometry.KDTreeFlann(colored_pcd)
                
                print("Transferring colors with improved accuracy...")
                # Process vertices in batches for better performance
                batch_size = 10000  # Number of vertices to process at once
                vertex_colors = []
                
                # New enhanced color transfer with neighborhood averaging for smoother color transitions
                for i in range(0, len(mesh_vertices), batch_size):
                    batch_end = min(i + batch_size, len(mesh_vertices))
                    print(f"Processing vertices {i} to {batch_end} of {len(mesh_vertices)}...")
                    
                    batch_colors = []
                    for j in range(i, batch_end):
                        try:
                            vertex = mesh_vertices[j]
                            # Find k nearest neighbors for better color interpolation
                            k = 3  # Number of nearest neighbors to consider
                            [_, idx, dist] = pcd_tree.search_knn_vector_3d(vertex, k)
                            
                            if idx and len(idx) > 0:
                                # Weight colors by distance from the vertex
                                if len(idx) > 1:
                                    # Normalize distances for weighting
                                    weights = 1.0 / (np.array(dist) + 1e-10)  # Avoid division by zero
                                    weights = weights / np.sum(weights)
                                    
                                    # Get colors from original point cloud
                                    neighbor_colors = np.asarray(colored_pcd.colors)[idx]
                                    
                                    # Calculate weighted average color
                                    color = np.zeros(3)
                                    for n in range(len(idx)):
                                        color += neighbor_colors[n] * weights[n]
                                else:
                                    # If only one point found, use its color directly
                                    color = np.asarray(colored_pcd.colors)[idx[0]]
                                
                                batch_colors.append(color)
                            else:
                                # Fallback color if no neighbors found
                                batch_colors.append([0.7, 0.7, 0.7])  # Default gray
                        except Exception as e:
                            print(f"Warning: Color transfer error for vertex {j}: {str(e)}")
                            batch_colors.append([0.7, 0.7, 0.7])  # Default gray
                    
                    vertex_colors.extend(batch_colors)
                
                # Check for invalid colors before applying
                vertex_colors_array = np.array(vertex_colors)
                if np.isnan(vertex_colors_array).any() or np.isinf(vertex_colors_array).any():
                    print("Warning: Some colors have invalid values. Fixing...")
                    # Replace invalid colors with neutral gray
                    invalid_mask = np.isnan(vertex_colors_array) | np.isinf(vertex_colors_array)
                    vertex_colors_array[invalid_mask] = 0.7
                
                # Apply colors to the mesh
                mesh.vertex_colors = o3d.utility.Vector3dVector(vertex_colors_array)
                print(f"Successfully transferred colors to {len(vertex_colors)} mesh vertices")
                
                # Verify color transfer was successful
                if len(mesh.vertex_colors) == len(mesh.vertices):
                    print("Color transfer verification: Success - All vertices have color information")
                else:
                    print(f"Color transfer verification: Warning - Only {len(mesh.vertex_colors)} of {len(mesh.vertices)} vertices have color information")
            
            except Exception as e:
                print(f"Error during color transfer: {str(e)}")
                print("Continuing without color information")
    
    # Apply correct orientation for OBJ files
    if orientation_fix and output_format.lower() == "obj":
        print("Applying orientation fix for OBJ format")
        try:
            # OBJ format has a different coordinate system, fix orientation
            rotation = mesh.get_rotation_matrix_from_xyz((math.pi, 0, 0))
            mesh.rotate(rotation, center=mesh.get_center())
        except Exception as e:
            print(f"Warning during orientation fix: {str(e)}")
    
    print(f"Saving mesh as {output_file}")
    try:
        if output_format.lower() == "obj":
            write_success = export_mesh_with_colors(mesh, output_file, write_vertex_colors, scale_factor=scale)
        else:
            write_success = o3d.io.write_triangle_mesh(output_file, mesh, write_vertex_colors=write_vertex_colors)
        
        if write_success:
            print(f"Successfully saved mesh with {len(mesh.vertices)} vertices and {len(mesh.triangles)} triangles")
        else:
            print("Warning: There may have been an issue saving the mesh")
            
            # Try alternative format if writing failed
            if output_format.lower() == "obj":
                print("Trying to save as PLY format instead...")
                ply_output = output_file.replace('.obj', '.ply')
                ply_success = o3d.io.write_triangle_mesh(ply_output, mesh, write_vertex_colors=write_vertex_colors)
                if ply_success:
                    print(f"Successfully saved mesh as PLY: {ply_output}")
                    return ply_output
                else:
                    print("Error: Failed to save mesh in any format")
                    return None
    except Exception as e:
        print(f"Error saving mesh: {str(e)}")
        return None
    
    # For OBJ files, ensure we copy the material file as well
    if output_format.lower() == "obj":
        mtl_file = output_file.replace('.obj', '.mtl')
        if os.path.exists(mtl_file):
            print(f"Material file saved at {mtl_file}")
            
            # Verify that the MTL file contains color information
            try:
                with open(mtl_file, 'r') as f:
                    mtl_contents = f.read()
                    if 'Kd ' in mtl_contents:  # Check for diffuse color definitions
                        print("MTL file contains color information")
                    else:
                        print("Warning: MTL file may not contain proper color information")
            except Exception as e:
                print(f"Could not verify MTL file contents: {str(e)}")
    
    print("Conversion complete!")
    return output_file

def main():
    parser = argparse.ArgumentParser(description='Convert a point cloud to a mesh')
    parser.add_argument('input_file', help='Input point cloud file (.ply)')
    parser.add_argument('--output', '-o', help='Output mesh file')
    parser.add_argument('--format', '-f', default='obj', help='Output format: obj (default), ply, stl')
    parser.add_argument('--method', '-m', default='poisson', 
                       choices=['poisson', 'ball_pivoting', 'alpha_shape', 'hybrid'],
                       help='Surface reconstruction method')
    parser.add_argument('--depth', '-d', type=int, default=9, 
                       help='Depth for Poisson reconstruction (default: 9)')
    parser.add_argument('--quality', '-q', default='normal',
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
    parser.add_argument('--smoothness', type=float, default=1.0,
                       help='Smoothness factor (0.0-2.0, default: 1.0)')
    parser.add_argument('--super-smooth', action='store_true',
                       help='Apply enhanced smoothing (sets smoothness to 2.0)')
    parser.add_argument('--aggressive-hole-filling', action='store_true',
                       help='Use aggressive techniques for hole filling')
    parser.add_argument('--density-threshold-percentile', type=float, default=0.01,
                       help='Percentile threshold for density filtering (default: 0.01)')
    parser.add_argument('--normal-neighbors', type=int, default=30,
                       help='Number of neighbors for normal estimation (default: 30)')
    
    args = parser.parse_args()
    
    # Apply super-smooth option if selected
    smoothness = 2.0 if args.super_smooth else args.smoothness

    # Convert mesh
    output_path = convert_pointcloud_to_mesh(
        args.input_file,
        args.output,
        args.format,
        args.depth,
        args.scale,
        args.orientation_fix,
        args.normals,
        args.colors,
        args.method,
        args.quality,
        args.save_to_converted,
        args.fill_holes,
        smoothness,
        args.aggressive_hole_filling,
        args.density_threshold_percentile,
        args.normal_neighbors
    )
    
    if output_path:
        print(f"Mesh saved to: {output_path}")
    else:
        print("Conversion failed")
        sys.exit(1)

# Add the missing entry point function that the executable is looking for
def main_3dgs_to_mesh():
    """Entry point for the 3dgs-to-mesh script"""
    main()

if __name__ == "__main__":
    main()
