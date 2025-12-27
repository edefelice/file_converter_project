"""
File Handler Module
Handles file operations (upload, download, validation)

Branch: insecure
Contains intentional vulnerabilities for educational purposes.

WARNING: Do NOT use in production!
"""

import os

class FileHandler:
    """
    Handles file operations for the application - INSECURE VERSION

    VULNERABILITIES:
    - A01: Broken Access Control - No path validation (Path Traversal)
    - A04: Insecure Design - Insufficient validation
    """

    def __init__(self, upload_folder, converted_folder):
        """
        Initialize the file handler

        Args:
            upload_folder: Directory for uploaded files
            converted_folder: Directory for converted files
        """
        self.upload_folder = upload_folder
        self.converted_folder = converted_folder
    
    def get_file_path(self, filename, folder='upload'):
        """
        Get full path for a file

        VULNERABILITY A01: Broken Access Control (Path Traversal)
        No validation of filename - allows directory traversal attacks

        Attack example:
            filename = "../../../etc/passwd"
            Returns: "uploads/../../../etc/passwd" -> "/etc/passwd"

        Args:
            filename: Name of the file
            folder: 'upload' or 'converted'
        
        Returns:
            Full file path (potentially outside intended directory!)
        """
        # VULNERABILITY: NO PATH SANITIZATION!
        if folder == 'converted':
            return os.path.join(self.converted_folder, filename)
        else:
            return os.path.join(self.upload_folder, filename)
    
    def file_exists(self, filename, folder='upload'):
        """
        Check if file exists

        Args:
            filename: Name of the file
            folder: 'upload' or 'converted'
        
        Returns:
            Boolean
        """
        filepath = self.get_file_path(filename, folder)
        return os.path.exists(filepath)
    
    def delete_file(self, filename, folder='upload'):
        """
        Delete a file

        VULNERABILITY A01: Broken Access Control
        Can delete ANY file on the system using path traversal

        Attack example:
            filename = "../../../important_file.txt"
            Deletes file outside intended directory!

        Args:
            filename: Name of the file to delete (UNSANITIZED!)
            folder: 'upload' or 'converted'
        
        Returns:
            Boolean indicating success
        """
        filepath = self.get_file_path(filename, folder)

        try:
            # No validation - can delete system files!
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def list_files(self, folder='upload'):
        """
        List all files in a folder

        Args:
            folder: 'upload' or 'converted'
        
        Returns:
            List of filenames
        """
        target_folder = self.converted_folder if folder == 'converted' else self.upload_folder

        try:
            return os.listdir(target_folder)
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def get_file_size(self, filename, folder='upload'):
        """
        Get file size in bytes

        Args:
            filename: Name of the file
            folder: 'upload' or 'converted'
        
        Returns:
            File size in bytes or None if error
        """
        filepath = self.get_file_path(filename, folder)

        try:
            return os.path.getsize(filepath)
        except Exception as e:
            print(f"Error getting file size: {e}")
            return None