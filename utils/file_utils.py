"""
File utility functions for Algebra Visualizer Pro
"""

import os
import json
import csv
import tempfile
from datetime import datetime
from typing import Any, Dict, List
import pandas as pd
import streamlit as st

def save_plot_image(fig, filename: str, format: str = "png") -> str:
    """
    Save plotly figure as image file
    
    Args:
        fig: Plotly figure object
        filename: Output filename
        format: Image format (png, jpeg, svg, pdf)
        
    Returns:
        Path to saved file
    """
    try:
        # Create temp directory if it doesn't exist
        temp_dir = tempfile.gettempdir()
        output_dir = os.path.join(temp_dir, "algebra_visualizer")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate full file path
        file_path = os.path.join(output_dir, f"{filename}.{format}")
        
        # Save the figure
        if hasattr(fig, 'write_image'):
            fig.write_image(file_path, format=format)
        else:
            # Fallback for matplotlib figures
            import matplotlib.pyplot as plt
            fig.savefig(file_path, format=format, bbox_inches='tight')
            plt.close(fig)
        
        return file_path
    except Exception as e:
        st.error(f"Error saving plot: {e}")
        return ""

def export_dataframe(df: pd.DataFrame, filename: str, format: str = "csv") -> str:
    """
    Export pandas DataFrame to file
    
    Args:
        df: DataFrame to export
        filename: Output filename
        format: Export format (csv, excel, json)
        
    Returns:
        Path to exported file
    """
    try:
        temp_dir = tempfile.gettempdir()
        output_dir = os.path.join(temp_dir, "algebra_visualizer")
        os.makedirs(output_dir, exist_ok=True)
        
        file_path = os.path.join(output_dir, f"{filename}.{format}")
        
        if format == "csv":
            df.to_csv(file_path, index=False)
        elif format == "excel":
            df.to_excel(file_path, index=False)
        elif format == "json":
            df.to_json(file_path, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return file_path
    except Exception as e:
        st.error(f"Error exporting data: {e}")
        return ""

def read_uploaded_file(uploaded_file) -> Any:
    """
    Read uploaded file based on its type
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        File content (DataFrame, dict, or string)
    """
    try:
        if uploaded_file.type == "text/csv":
            return pd.read_csv(uploaded_file)
        elif uploaded_file.type == "application/json":
            return json.load(uploaded_file)
        elif uploaded_file.type in ["text/plain", "application/octet-stream"]:
            return uploaded_file.getvalue().decode("utf-8")
        else:
            st.warning(f"Unsupported file type: {uploaded_file.type}")
            return None
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

def create_backup(file_path: str, backup_dir: str = None) -> str:
    """
    Create backup of a file
    
    Args:
        file_path: Path to file to backup
        backup_dir: Backup directory
        
    Returns:
        Path to backup file
    """
    if not os.path.exists(file_path):
        return ""
    
    if backup_dir is None:
        backup_dir = os.path.join(os.path.dirname(file_path), "backups")
    
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename with timestamp
    filename = os.path.basename(file_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{filename}.backup_{timestamp}"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        st.error(f"Error creating backup: {e}")
        return ""

def clean_old_files(directory: str, pattern: str = "*", max_age_days: int = 7) -> int:
    """
    Clean old files from directory
    
    Args:
        directory: Directory to clean
        pattern: File pattern to match
        max_age_days: Maximum file age in days
        
    Returns:
        Number of files deleted
    """
    if not os.path.exists(directory):
        return 0
    
    import glob
    from datetime import datetime, timedelta
    
    files = glob.glob(os.path.join(directory, pattern))
    cutoff_time = datetime.now() - timedelta(days=max_age_days)
    deleted_count = 0
    
    for file_path in files:
        if os.path.isfile(file_path):
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time < cutoff_time:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except OSError:
                    pass  # Skip files that can't be deleted
    
    return deleted_count

def ensure_directory(directory: str) -> bool:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory: Directory path
        
    Returns:
        True if directory exists or was created
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except OSError as e:
        st.error(f"Error creating directory {directory}: {e}")
        return False

def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get information about a file
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with file information
    """
    if not os.path.exists(file_path):
        return {}
    
    stat = os.stat(file_path)
    
    return {
        "size": stat.st_size,
        "created": datetime.fromtimestamp(stat.st_ctime),
        "modified": datetime.fromtimestamp(stat.st_mtime),
        "extension": os.path.splitext(file_path)[1],
        "filename": os.path.basename(file_path)
    }