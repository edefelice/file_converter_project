"""
File Converter Module
Handles file format conversions

Branch: insecure
Contains COMMAND INJECTION vulnerability (A03)
"""

import os
import subprocess

class FileConverter:
    """
    Handles file conversions

    CRITICAL VULNERABILITY: Command Injection (A03)
    User input is passed directly to shell commands without sanitization
    """

    def __init__(self):
        """ Initialize the converter"""
        self.supported_formats = ['pdf', 'txt', 'png', 'jpg']
    
    def convert(self, filename, output_format, input_folder, output_folder):
        """
        Convert file to specified format

        VULNERABILITY A03: COMMAND INJECTION
        Filename and format are used in shell commands without sanitization!

        Example attack:
            filename = "file.txt; rm -rf /"
            This would execute: convert file.txt output.pdf; rm -rf /
        
        Args:
            filename: Input filename
            output_format: Desired output format
            input_folder: Folder containing input file
            output_folder: Folder for output file
        
        Returns:
            Dictionary with result information
        """
        # NO INPUT SANITIZATION!
        input_path = os.path.join(input_folder, filename)
        output_filename = self._generate_output_filename(filename, output_format)
        output_path = os.path.join(output_folder, output_filename)

        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {filename}")
        
        # COMMAND INJECTION VULNERABILITY!
        # Using os.system() with unsanitized user input
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
        Execute the actual conversion command

        CRITICAL VULNERABILITY: Command Injection

        Args:
            input_path: Full path to input file
            output_path: Full path to output file
            output_format: Target format
        
        Returns:
            Boolean indicating success
        """
        try:
            # COMMAND INJECTION HERE!
            # User-controlled input is directly interpolated into shell command
            if output_format == 'pdf':
                # Simulated conversion command
                # Vulnerable to injection: filename could be "file.txt; malicious_command"
                command = f"echo 'Converting {input_path} to PDF' > {output_path}"
            elif output_format == 'txt':
                command = f"cat {input_path} > {output_path}"
            elif output_format in ['png', 'jpg']:
                command = f"cp {input_path} {output_path}"
            else:
                # Default fallback
                command = f"cp {input_path} {output_path}"
            
            # DANGEROUS: Executing shell command with user input!
            # Using os.system() which executes commands in a shell
            result = os.system(command)

            return result == 0
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
        