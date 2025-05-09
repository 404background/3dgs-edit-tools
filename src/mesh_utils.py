"""
Mesh generation and processing utilities for 3DGS Editor.

This module contains common functions for mesh operations and
point cloud processing used in the 3DGS Editor library.
"""

import numpy as np
import os
from .utils import ensure_directory_exists, print_debug_info


def estimate_normals(points, k_neighbors=20, query_points=None):
    """
    Estimate normals for points in a point cloud.
    
    Args:
        points (numpy.ndarray): Array of 3D points (N x 3)
        k_neighbors (int): Number of neighbors to consider
        query_points (numpy.ndarray, optional): Points to estimate normals for
            
    Returns:
        numpy.ndarray: Estimated normals
    """
    try:
        import open3d as o3d
    except ImportError:
        raise ImportError("open3d is required for normal estimation. Install with: pip install open3d")
    
    # Convert points to Open3D format
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    
    # Estimate normals
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamKNN(k_neighbors))
    
    # Orient normals
    pcd.orient_normals_consistent_tangent_plane(k_neighbors)
    
    # Return normals for all points or query points
    normals = np.asarray(pcd.normals)
    if query_points is not None:
        # Find closest points and use their normals
        pcd_tree = o3d.geometry.KDTreeFlann(pcd)
        query_normals = np.zeros_like(query_points)
        
        for i, point in enumerate(query_points):
            _, idx, _ = pcd_tree.search_knn_vector_3d(point, 1)
            query_normals[i] = normals[idx[0]]
            
        return query_normals
    
    return normals


def create_mesh_with_method(points, normals, colors=None, method="poisson", 
                            quality="normal", density=0.01, 
                            smoothness=1.0, fill_holes=False, 
                            aggressive_holes=False, neighbors=30):
    """
    Create a mesh from points and normals using specified method.
    
    Args:
        points (numpy.ndarray): Array of 3D points
        normals (numpy.ndarray): Array of point normals
        colors (numpy.ndarray, optional): Array of point colors
        method (str): Mesh creation method ('poisson', 'ball_pivoting', 'alpha_shape', 'hybrid')
        quality (str): Quality preset ('low', 'normal', 'high', 'ultra')
        density (float): Density threshold percentile (0.001-0.05)
        smoothness (float): Strength of mesh smoothing (0.0-3.0)
        fill_holes (bool): Whether to fill holes in the mesh
        aggressive_holes (bool): Whether to use aggressive hole filling
        neighbors (int): Number of neighbors for reconstruction algorithms
        
    Returns:
        object: Open3D mesh object
    """
    try:
        import open3d as o3d
    except ImportError:
        raise ImportError("open3d is required for mesh creation. Install with: pip install open3d")
    
    # Convert quality preset to parameters
    quality_params = get_quality_preset(quality)
    poisson_depth = quality_params["poisson_depth"]
    
    # Create point cloud
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.normals = o3d.utility.Vector3dVector(normals)
    
    if colors is not None:
        # Ensure colors are in the right format (0-1 range)
        if colors.max() > 1.0:
            colors = colors / 255.0
        pcd.colors = o3d.utility.Vector3dVector(colors)
    
    # Apply different mesh reconstruction methods
    mesh = None
    
    if method == "poisson":
        print_debug_info(f"Creating mesh with Poisson reconstruction (depth={poisson_depth})")
        mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            pcd, depth=poisson_depth, width=0, scale=1.1, 
            linear_fit=False if fill_holes else True)
        
    elif method == "ball_pivoting":
        print_debug_info(f"Creating mesh with Ball Pivoting (neighbors={neighbors})")
        # Calculate appropriate radius based on average distance
        distances = np.asarray(pcd.compute_nearest_neighbor_distance())
        avg_dist = np.mean(distances)
        radii = [avg_dist*2, avg_dist*4, avg_dist*8]
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
            pcd, o3d.utility.DoubleVector(radii))
        
    elif method == "alpha_shape":
        print_debug_info(f"Creating mesh with Alpha Shape (neighbors={neighbors})")
        # Calculate appropriate alpha based on average distance
        distances = np.asarray(pcd.compute_nearest_neighbor_distance())
        avg_dist = np.mean(distances)
        alpha = avg_dist * 3
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(
            pcd, alpha)
        
    elif method == "hybrid":
        print_debug_info(f"Creating mesh with Hybrid method (poisson={poisson_depth}, neighbors={neighbors})")
        # Create both poisson and ball pivoting meshes and combine them
        mesh_poisson, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            pcd, depth=poisson_depth, width=0, scale=1.1, 
            linear_fit=False if fill_holes else True)
        
        # Calculate appropriate radius based on average distance
        distances = np.asarray(pcd.compute_nearest_neighbor_distance())
        avg_dist = np.mean(distances)
        radii = [avg_dist*2, avg_dist*4, avg_dist*8]
        
        mesh_bp = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
            pcd, o3d.utility.DoubleVector(radii))
        
        # Combine meshes
        mesh = mesh_poisson + mesh_bp
        mesh.remove_duplicated_vertices()
        mesh.remove_duplicated_triangles()
        
    else:
        print_debug_info(f"Unknown mesh creation method: {method}. Using Poisson reconstruction.")
        mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            pcd, depth=8, width=0, scale=1.1, linear_fit=True)
    
    # Post-processing
    if mesh is not None:
        # Remove low density vertices if density is specified
        if density < 0.05:
            print_debug_info(f"Filtering with density threshold: {density}")
            mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
                pcd, depth=poisson_depth)
            vertices_to_remove = densities < np.quantile(densities, density)
            mesh.remove_vertices_by_mask(vertices_to_remove)
        
        # Apply smoothing if requested
        if smoothness > 0:
            print_debug_info(f"Applying smoothing (strength={smoothness})")
            iterations = int(smoothness * 2)
            for _ in range(iterations):
                mesh = mesh.filter_smooth_taubin(number_of_iterations=1)
        
        # Fill holes if requested
        if fill_holes:
            print_debug_info("Filling holes")
            mesh.fill_holes()
            
            if aggressive_holes:
                print_debug_info("Applying aggressive hole filling")
                max_hole_size = 100 if quality == "ultra" else 50
                mesh.fill_holes(max_hole_size)
    
    return mesh


def get_quality_preset(quality):
    """
    Get parameters for a quality preset.
    
    Args:
        quality (str): Quality preset ('low', 'normal', 'high', 'ultra')
        
    Returns:
        dict: Dictionary of quality parameters
    """
    presets = {
        "low": {
            "poisson_depth": 8,
            "normal_neighbors": 20,
            "mesh_neighbors": 20,
        },
        "normal": {
            "poisson_depth": 9,
            "normal_neighbors": 30,
            "mesh_neighbors": 30,
        },
        "high": {
            "poisson_depth": 10,
            "normal_neighbors": 40,
            "mesh_neighbors": 40,
        },
        "ultra": {
            "poisson_depth": 11,
            "normal_neighbors": 50,
            "mesh_neighbors": 60,
        }
    }
    
    # Default to "normal" if preset not found
    if quality not in presets:
        print_debug_info(f"Unknown quality preset: {quality}. Using 'normal' preset.")
        return presets["normal"]
    
    return presets[quality]


def save_mesh(mesh, output_file, texture=None):
    """
    Save mesh to a file.
    
    Args:
        mesh: Open3D mesh object
        output_file (str): Output file path
        texture (numpy.ndarray, optional): Texture image data
        
    Returns:
        str: Path to the saved file
    """
    try:
        import open3d as o3d
    except ImportError:
        raise ImportError("open3d is required for saving meshes. Install with: pip install open3d")
    
    # Ensure output directory exists
    ensure_directory_exists(output_file)
    
    # Determine export format from extension
    ext = os.path.splitext(output_file)[1].lower()
    
    if ext == ".obj":
        # Save as OBJ with material file
        material_file = os.path.splitext(output_file)[0] + ".mtl"
        success = o3d.io.write_triangle_mesh(output_file, mesh, 
                                           write_triangle_uvs=True,
                                           write_vertex_colors=True)
    else:
        # Save in other formats
        success = o3d.io.write_triangle_mesh(output_file, mesh)
    
    if not success:
        print_debug_info(f"Warning: Failed to write mesh to {output_file}")
    else:
        print_debug_info(f"Mesh saved to {output_file}")
    
    return output_file
