"""
3D transformation utilities for 3DGS Editor.

This module contains common functions for 3D transformations and
operations used in the 3DGS Editor library.
"""

import numpy as np
import math


def quaternion_to_rotation_matrix(qx, qy, qz, qw):
    """
    Convert a quaternion to a rotation matrix.
    
    Args:
        qx, qy, qz, qw: Quaternion components
        
    Returns:
        numpy.ndarray: 3x3 rotation matrix
    """
    # Normalize quaternion
    q = np.array([qx, qy, qz, qw], dtype=float)
    q = q / np.linalg.norm(q)
    
    qx, qy, qz, qw = q
    
    # Compute rotation matrix
    r00 = 1 - 2*qy**2 - 2*qz**2
    r01 = 2*qx*qy - 2*qz*qw
    r02 = 2*qx*qz + 2*qy*qw
    
    r10 = 2*qx*qy + 2*qz*qw
    r11 = 1 - 2*qx**2 - 2*qz**2
    r12 = 2*qy*qz - 2*qx*qw
    
    r20 = 2*qx*qz - 2*qy*qw
    r21 = 2*qy*qz + 2*qx*qw
    r22 = 1 - 2*qx**2 - 2*qy**2
    
    return np.array([
        [r00, r01, r02],
        [r10, r11, r12],
        [r20, r21, r22]
    ])


def rotation_matrix_to_quaternion(R):
    """
    Convert a rotation matrix to a quaternion.
    
    Args:
        R (numpy.ndarray): 3x3 rotation matrix
        
    Returns:
        tuple: (qx, qy, qz, qw) - Quaternion components
    """
    # Check if the input is a 3x3 matrix
    if R.shape != (3, 3):
        raise ValueError("Input must be a 3x3 rotation matrix")
    
    trace = np.trace(R)
    
    if trace > 0:
        S = 2.0 * math.sqrt(trace + 1.0)
        qw = 0.25 * S
        qx = (R[2, 1] - R[1, 2]) / S
        qy = (R[0, 2] - R[2, 0]) / S
        qz = (R[1, 0] - R[0, 1]) / S
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        S = 2.0 * math.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2])
        qw = (R[2, 1] - R[1, 2]) / S
        qx = 0.25 * S
        qy = (R[0, 1] + R[1, 0]) / S
        qz = (R[0, 2] + R[2, 0]) / S
    elif R[1, 1] > R[2, 2]:
        S = 2.0 * math.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2])
        qw = (R[0, 2] - R[2, 0]) / S
        qx = (R[0, 1] + R[1, 0]) / S
        qy = 0.25 * S
        qz = (R[1, 2] + R[2, 1]) / S
    else:
        S = 2.0 * math.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])
        qw = (R[1, 0] - R[0, 1]) / S
        qx = (R[0, 2] + R[2, 0]) / S
        qy = (R[1, 2] + R[2, 1]) / S
        qz = 0.25 * S
    
    # Normalize quaternion
    q = np.array([qx, qy, qz, qw])
    q = q / np.linalg.norm(q)
    
    return tuple(q)


def rotation_matrix_from_euler(rx, ry, rz, order='xyz'):
    """
    Create a rotation matrix from Euler angles.
    
    Args:
        rx, ry, rz: Rotation angles in radians
        order: Order of rotations ('xyz', 'zyx', etc.)
        
    Returns:
        numpy.ndarray: 3x3 rotation matrix
    """
    # Rotation matrices for x, y, z axes
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(rx), -np.sin(rx)],
        [0, np.sin(rx), np.cos(rx)]
    ])
    
    Ry = np.array([
        [np.cos(ry), 0, np.sin(ry)],
        [0, 1, 0],
        [-np.sin(ry), 0, np.cos(ry)]
    ])
    
    Rz = np.array([
        [np.cos(rz), -np.sin(rz), 0],
        [np.sin(rz), np.cos(rz), 0],
        [0, 0, 1]
    ])
    
    # Combine rotations based on specified order
    if order == 'xyz':
        return Rz @ Ry @ Rx
    elif order == 'zyx':
        return Rx @ Ry @ Rz
    elif order == 'xzy':
        return Ry @ Rz @ Rx
    elif order == 'yxz':
        return Rz @ Rx @ Ry
    elif order == 'yzx':
        return Rx @ Rz @ Ry
    elif order == 'zxy':
        return Ry @ Rx @ Rz
    else:
        raise ValueError(f"Invalid rotation order: {order}")


def create_rotation_matrix(angle_x=0, angle_y=0, angle_z=0):
    """
    Create a rotation matrix from angles (in degrees).
    
    Args:
        angle_x, angle_y, angle_z: Rotation angles in degrees
        
    Returns:
        numpy.ndarray: 3x3 rotation matrix
    """
    # Convert degrees to radians
    rx = math.radians(angle_x)
    ry = math.radians(angle_y)
    rz = math.radians(angle_z)
    
    return rotation_matrix_from_euler(rx, ry, rz)


def create_scaling_matrix(scale_x, scale_y, scale_z):
    """
    Create a scaling matrix.
    
    Args:
        scale_x, scale_y, scale_z: Scaling factors
        
    Returns:
        numpy.ndarray: 3x3 scaling matrix
    """
    return np.array([
        [scale_x, 0, 0],
        [0, scale_y, 0],
        [0, 0, scale_z]
    ])


def create_translation_vector(dx, dy, dz):
    """
    Create a translation vector.
    
    Args:
        dx, dy, dz: Translation distances
        
    Returns:
        numpy.ndarray: Translation vector
    """
    return np.array([dx, dy, dz])


def apply_transformation(points, rotation=None, scaling=None, translation=None):
    """
    Apply transformation to a set of points.
    
    Args:
        points (numpy.ndarray): Array of 3D points
        rotation (numpy.ndarray): 3x3 rotation matrix
        scaling (numpy.ndarray): 3x3 scaling matrix
        translation (numpy.ndarray): Translation vector
        
    Returns:
        numpy.ndarray: Transformed points
    """
    transformed_points = points.copy()
    
    # Apply scaling if provided
    if scaling is not None:
        transformed_points = transformed_points @ scaling.T
    
    # Apply rotation if provided
    if rotation is not None:
        transformed_points = transformed_points @ rotation.T
    
    # Apply translation if provided
    if translation is not None:
        transformed_points = transformed_points + translation
    
    return transformed_points
