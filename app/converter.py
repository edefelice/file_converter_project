"""
File Converter Module
Handles file format conversions

Branch: insecure
Contains COMMAND INJECTION vulnerability (A03)
"""

import os
import subprocess
import shlex

class FileConverter:
    """
    Handles file conversions - SECURE VERSION

    CRITICAL VULNERABILITY: Command Injection (A03)
    FIX: Using subprocess with argument lists instead of shell=True
    """

    def __init__(self):
        """ Initialize the converter"""
        self.supported_formats = ['pdf', 'txt', 'png', 'jpg']
    
    def convert(self, filename, output_format, input_folder, output_folder):
        """
        Convert file to specified format

        VULNERABILITY A03: COMMAND INJECTION
        FIX: Input validation and safe subprocess usage
        
        Args:
            filename: Input filename
            output_format: Desired output format
            input_folder: Folder containing input file
            output_folder: Folder for output file
        
        Returns:
            Dictionary with result information
        """
        # FIX: Validate output format against whitelist
        if output_format not in self.supported_formats:
            raise ValueError(f"Unsupported format: {output_format}")

        # FIX: Validate filename (no path traversal)
        if '..' in filename or filename.startswith('/'):
            raise ValueError("Invalid filename")
        
        # FIX: Use secure filename handling
        safe_filename = os.path.basename(filename)
        input_path = os.path.join(input_folder, safe_filename)
        output_filename = self._generate_output_filename(safe_filename, output_format)
        output_path = os.path.join(output_folder, output_filename)

        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {safe_filename}")
        
        # COMMAND INJECTION VULNERABILITY!
        # FIX: Safe command execution
        success = self._execute_conversion(input_path, output_path, output_format)

        if success:
            return {
                'success': True,
                'message': 'File converted successfully',
                'output_file': output_filename,
                'output_path': output_path
            }
        else:
            raise Exception("Conversion failed")

    def _generate_output_filename(self, input_filename, output_format):
        """
        Generate output filename

        Args:
            input_filename: Original filename
            output_format: Desired format
        
        Returns:
            Output filename
        """
        # Remove extension and add new one
        base_name = os.path.splitext(input_filename)[0]
        return f"{base_name}.{output_format}"
    
    def _execute_conversion(self, input_path, output_path, output_format):
        """
        Execute the actual conversion command - SECURE VERSION

        CRITICAL VULNERABILITY: Command Injection
        FIX: Using subprocess.run() with argument lists
        - No shell=True
        - Arguments passed as list (not string)
        - Cannot inject commands

        Args:
            input_path: Full path to input file
            output_path: Full path to output file
            output_format: Target format
        
        Returns:
            Boolean indicating success
        """
        try:
            # COMMAND INJECTION HERE!
            # FIX: Using subprocess.run with list arguments (NO SHELL)
            if output_format == 'pdf':
                # Simulated conversion command
                # Safe: arguments are separate list items
                result = subprocess.run(
                    ['sh', '-c', 'echo "Converting to PDF" > "$1"', '_', output_path],
                    capture_output=True,
                    timeout=30
                )
            elif output_format == 'txt':
                result = subprocess.run(
                    ['cp', 'input_path', output_path],
                    capture_output=True,
                    timeout=30
                )
            elif output_format in ['png', 'jpg']:
                result = subprocess.run(
                    ['cp', 'input_path', output_path],
                    capture_output=True,
                    timeout=30
                )
            else:
                # Default fallback
                return False
            
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("Conversion timeout")
            return False
        except Exception as e:
            print(f"Conversion error: {e}")
            return False
    
    def is_format_supported(self, format_name):
        """
        Check if format is supported

        Args:
            format_name: Format to check
        
        Returns:
            Boolean
        """
        return format_name.lower() in self.supported_formats
        