"""
File Handler Module
Handles file operations (upload, download, validation)

Branch: main (secure)
Vulnerabilities FIXED.
"""

import os
from werkzeug.utils import secure_filename

class FileHandler:
    """
    Handles file operations for the application - SECURE VERSION

    VULNERABILITIES FIXED:
    - A01: Broken Access Control - No path validation
    - A04: Insecure Design - Insufficient validation

    FIX: Path validation on all operations
    """

    def __init__(self, upload_folder, converted_folder):
        """
        Initialize the file handler

        Args:
            upload_folder: Directory for uploaded files
            converted_folder: Directory for converted files
        """
        self.upload_folder = os.path.abspath(upload_folder)
        self.converted_folder = os.path.abspath(converted_folder)
    
    def _get_base_folder(self, folder):
        """Get the base folder path"""
        if folder == 'converted':
            return self.converted_folder
        return self.upload_folder

    def _is_safe_path(self, base_folder, filename):
        """
        FIX A01: Validate path to prevent directory traversal

        Args:
            base_folder: The allowed base directory
            filename: The filename to validate
        
        Returns:
            Boolean indicating if path is safe
        """
        # Resolve the absolute path
        abs_path = os.path.abspath(os.path.join(base_folder, filename))

        # Check if the resolved path starts with the base directory
        return abs_path.startswith(base_folder)
    
    def get_file_path(self, filename, folder='upload'):
        """
        Get full path for a file - SECURE VERSION

        FIX VULNERABILITY A01: Broken Access Control (Path Traversal)
        Validates path to prevent directory traversal

        Args:
            filename: Name of the file
            folder: 'upload' or 'converted'
        
        Returns:
            Full file path or None if invalid
        """

        # FIXED No Path Sanitization: Sanitize filename
        safe_filename = secure_filename(filename)
        if not safe_filename:
            return None
        
        base_folder = self._get_base_folder(folder)

        # FIX: Validate if path is within allowed directory
        if not self._is_safe_path(base_folder, safe_filename):
            return None
        
        return os.path.join(base_folder, safe_filename)
    
    def file_exists(self, filename, folder='upload'):
        """
        Check if file exists - SECURE VERSION

        Args:
            filename: Name of the file
            folder: 'upload' or 'converted'
        
        Returns:
            Boolean
        """
        filepath = self.get_file_path(filename, folder)
        if filepath is None:
            return False

        return os.path.exists(filepath)
    
    def delete_file(self, filename, folder='upload'):
        """
        Delete a file - SECURE VERSION

        FIX A01: Path Validation prevents arbitrary file deletion

        Args:
            filename: Name of the file to delete
            folder: 'upload' or 'converted'
        
        Returns:
            Boolean indicating success
        """
        filepath = self.get_file_path(filename, folder)

        # FIX: Check if path is valid
        if filepath is None:
            return False

        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception:
            return False
    
    def list_files(self, folder='upload'):
        """
        List all files in a folder

        Args:
            folder: 'upload' or 'converted'
        
        Returns:
            List of filenames
        """
        target_folder = self._get_base_folder(folder)

        try:
            return os.listdir(target_folder)
        except Exception:
            return []
    
    def get_file_size(self, filename, folder='upload'):
        """
        Get file size in bytes - SECURE VERSION

        Args:
            filename: Name of the file
            folder: 'upload' or 'converted'
        
        Returns:
            File size in bytes or None if error
        """
        filepath = self.get_file_path(filename, folder)

        if filepath is None:
            return None

        try:
            return os.path.getsize(filepath)
        except Exception:
            return None