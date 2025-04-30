import numpy as np


# Constants for color identification
SH_COLOR_PROPERTIES = ['f_dc_0', 'f_dc_1', 'f_dc_2']
STANDARD_COLOR_PROPERTIES = [
    ('red', 'green', 'blue'),
    ('r', 'g', 'b'),
]

# Global variable to store SH color range
sh_color_range = {
    'min': -3.0,  # Previously: -1.0, before that: -0.5
    'max': 3.0,   # Previously: 1.0, before that: 0.5
    'is_initialized': False
}


def detect_color_properties(properties):
    """
    Detect color-related property indices from a property list
    
    Args:
        properties (list): List of property names
        
    Returns:
        tuple: (r_idx, g_idx, b_idx, is_sh_color) - Color-related indices and
               a flag indicating whether it's a spherical harmonic (SH) color format
    """
    r_idx = g_idx = b_idx = None
    is_sh_color = False
    
    # Check for SH color format
    try:
        r_idx = properties.index('f_dc_0')
        g_idx = properties.index('f_dc_1')
        b_idx = properties.index('f_dc_2')
        is_sh_color = True
        return r_idx, g_idx, b_idx, is_sh_color
    except ValueError:
        pass
    
    # Check for standard color format
    for r_name, g_name, b_name in STANDARD_COLOR_PROPERTIES:
        try:
            r_idx = properties.index(r_name)
            g_idx = properties.index(g_name)
            b_idx = properties.index(b_name)
            return r_idx, g_idx, b_idx, is_sh_color
        except ValueError:
            continue
            
    return r_idx, g_idx, b_idx, is_sh_color


def get_color_value_range(colors):
    """
    Safely calculate the range of color values
    
    Args:
        colors (list): List of colors [[r, g, b], ...]
        
    Returns:
        tuple: (min_val, max_val, is_signed) - Minimum color value, maximum color value,
               and whether negative values are included
    """
    if not colors or len(colors) == 0:
        return 0.0, 1.0, False
    
    try:
        # Safely calculate min/max values avoiding empty sequences
        min_val = min(
            min(c[0] for c in colors if c[0] is not None),
            min(c[1] for c in colors if c[1] is not None),
            min(c[2] for c in colors if c[2] is not None)
        )
        max_val = max(
            max(c[0] for c in colors if c[0] is not None),
            max(c[1] for c in colors if c[1] is not None),
            max(c[2] for c in colors if c[2] is not None)
        )
        is_signed = min_val < 0
    except ValueError:
        # Default values if min/max fail
        min_val = 0.0
        max_val = 1.0
        is_signed = False
    
    # Ensure valid range for scaling
    if max_val <= min_val:
        max_val = min_val + 1.0
    
    return min_val, max_val, is_signed


def store_sh_color_range(min_val, max_val):
    """
    Store SH color range globally
    
    Args:
        min_val (float): Minimum value
        max_val (float): Maximum value
    """
    global sh_color_range
    sh_color_range['min'] = min_val
    sh_color_range['max'] = max_val
    sh_color_range['is_initialized'] = True
    print(f"Stored SH color range: {min_val} to {max_val}")


def get_sh_color_range():
    """
    Get the stored SH color range
    
    Returns:
        tuple: (min_val, max_val, is_initialized) - Minimum and maximum SH color values and initialization status
    """
    global sh_color_range
    return sh_color_range['min'], sh_color_range['max'], sh_color_range['is_initialized']


def normalize_color_for_editing(color_values, is_sh_color=False):
    """
    Normalize color values to 0-1 range for editing
    
    Args:
        color_values (np.ndarray): Array of color values
        is_sh_color (bool): Whether the color is in spherical harmonic (SH) format
        
    Returns:
        tuple: (normalized_values, min_val, max_val, is_signed) - 
               Normalized values, original minimum value, maximum value, and whether it contains negative values
    """
    min_val = np.min(color_values)
    max_val = np.max(color_values)
    is_signed = min_val < 0
    
    normalized_values = color_values.copy()
    
    # If SH color, store the range
    if is_sh_color:
        store_sh_color_range(min_val, max_val)
    
    # Need to normalize if it contains negative values or values greater than 1.0
    if min_val < 0 or max_val > 1.0:
        if max_val > min_val:
            # Map from min_val-max_val to 0-1 range
            normalized_values = (color_values - min_val) / (max_val - min_val)
        else:
            # If there's no range, simply set to 0.5
            normalized_values = np.ones_like(color_values) * 0.5
    elif max_val > 0:
        # All positive and <= 1.0, but scale to maximize range utilization
        normalized_values = color_values / max_val
    
    return normalized_values, min_val, max_val, is_signed


def convert_standard_to_sh_color(colors, orig_min=None, orig_max=None):
    """
    Convert standard color values (0-1 or 0-255) to spherical harmonic (SH) coefficient range
    
    Args:
        colors (np.ndarray): Array of color values
        orig_min (float, optional): Original minimum value of SH coefficients (target range minimum)
        orig_max (float, optional): Original maximum value of SH coefficients (target range maximum)
        
    Returns:
        np.ndarray: Color values converted to SH color coefficients
    """
    # First, determine the color scale
    max_color = np.max(colors)
    
    # Normalize to 0-1 if in 0-255 range
    if max_color > 1.0:
        normalized = colors.astype(float) / 255.0
    else:
        normalized = colors.astype(float)
    
    # Get stored SH range (if not specified)
    if orig_min is None or orig_max is None:
        stored_min, stored_max, is_initialized = get_sh_color_range()
        # Use stored range if available
        if is_initialized:
            orig_min = stored_min if orig_min is None else orig_min
            orig_max = stored_max if orig_max is None else orig_max
        else:
            # Default values
            orig_min = -3.0 if orig_min is None else orig_min  # Previously: -1.0, before that: -0.5
            orig_max = 3.0 if orig_max is None else orig_max   # Previously: 1.0, before that: 0.5
    
    # Map from 0-1 to original SH range
    target_range = orig_max - orig_min
    sh_colors = normalized * target_range + orig_min
    
    return sh_colors


def convert_sh_to_standard_color(sh_colors, orig_min=None, orig_max=None, target_max=1.0):
    """
    Convert spherical harmonic (SH) coefficient values to standard color range (0-1, etc.)
    
    Args:
        sh_colors (np.ndarray): Array of SH color coefficients
        orig_min (float, optional): Original minimum value of SH coefficients
        orig_max (float, optional): Original maximum value of SH coefficients
        target_max (float): Target maximum value (1.0 or 255.0)
        
    Returns:
        np.ndarray: Color values converted to standard color format
    """
    # Get stored SH range (if not specified)
    if orig_min is None or orig_max is None:
        stored_min, stored_max, is_initialized = get_sh_color_range()
        # Use stored range if available
        if is_initialized:
            orig_min = stored_min if orig_min is None else orig_min
            orig_max = stored_max if orig_max is None else orig_max
        else:
            # Calculate from sh_colors if no range information
            orig_min = np.min(sh_colors) if orig_min is None else orig_min
            orig_max = np.max(sh_colors) if orig_max is None else orig_max
    
    if orig_max > orig_min:
        # Map from SH range to 0-1
        normalized = (sh_colors - orig_min) / (orig_max - orig_min)
    else:
        # If there's no range, use SH values directly (but clipped)
        normalized = np.clip(sh_colors, 0.0, 1.0)
    
    # Scale to target range (usually 0-1 or 0-255)
    colors = normalized * target_max
    
    return colors


def convert_colors_between_formats(colors, source_type, target_type, 
                                  is_sh_source=False, is_sh_target=False,
                                  orig_min=None, orig_max=None):
    """
    Convert colors between different formats
    
    Args:
        colors (np.ndarray): Array of color values
        source_type (str): Source color type ("float" or "uchar")
        target_type (str): Target color type ("float" or "uchar")
        is_sh_source (bool): Whether the source color is in SH coefficient format
        is_sh_target (bool): Whether the target color should be in SH coefficient format
        orig_min (float, optional): Original minimum value for SH coefficients
        orig_max (float, optional): Original maximum value for SH coefficients
        
    Returns:
        np.ndarray: Converted color values
    """
    result = colors.copy().astype(float)
    
    # Step 1: Convert from source format to normalized float (0-1)
    if source_type == "uchar" or (source_type == "float" and np.max(colors) > 1.0):
        # Normalize to 0-1 for uchar or float in 0-255 range
        result = result / 255.0
    elif is_sh_source:
        # Normalize to 0-1 range for SH coefficients
        result = convert_sh_to_standard_color(result, orig_min, orig_max)
    
    # Step 2: Convert from normalized values (0-1) to target format
    if is_sh_target:
        # Restore to original range if target is SH coefficients
        result = convert_standard_to_sh_color(result, orig_min, orig_max)
    elif target_type == "uchar":
        # Convert to 0-255 range and integers if target is uchar
        result = np.round(result * 255.0).astype(np.uint8)
    # Otherwise (target_type == "float"), keep as 0-1
    
    return result


def print_color_debug_info(colors, color_type="unknown", is_sh_color=False):
    """
    Display debug information about colors
    
    Args:
        colors (np.ndarray): Array of color values
        color_type (str): Type of color data
        is_sh_color (bool): Whether the color is in spherical harmonic (SH) format
    """
    if len(colors) == 0:
        print("No color data available")
        return
    
    min_val = np.min(colors)
    max_val = np.max(colors)
    avg_val = np.mean(colors)
    
    print(f"Color type: {color_type}, SH color: {is_sh_color}")
    print(f"Color range: min={min_val:.6f}, max={max_val:.6f}, avg={avg_val:.6f}")
    
    # Display sample colors
    if len(colors) > 0:
        sample_indices = [0]
        if len(colors) > 1:
            sample_indices.extend([len(colors)//4, len(colors)//2, (3*len(colors))//4, len(colors)-1])
        
        for idx in sample_indices[:min(5, len(colors))]:
            print(f"Sample color at {idx}: {colors[idx]}")
