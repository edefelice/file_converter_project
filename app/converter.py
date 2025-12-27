"""
File Converter Module
Handles file format conversions

Branch: insecure
Contains COMMAND INJECTION vulnerability (A03)

WARNING: This code contains intentional vulnerabilities for educational purposes.
Do NOT use in production!
"""

import os
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

class FileConverter:
    """
    Handles file conversions

    VULNERABILITY A03: Command Injection
    Uses os.system() with unsanitized user input for some conversions
    """

    def __init__(self):
        """ Initialize the converter"""
        self.supported_formats = ['pdf', 'txt', 'png', 'jpg']
        self.image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
        self.text_extensions = {'.txt', '.md', '.csv'}
    
    def convert(self, filename, output_format, input_folder, output_folder):
        """
        Convert file to specified format

        VULNERABILITY A03: COMMAND INJECTION
        - No input sanitization on filename
        - No validation on output_format
        - Filename passed directly to shell commands

        Example attack:
            filename = "file.txt; rm -rf /"
            Results in: os.system("cp uploads/test.txt; rm -rf / converted/test.txt")
        
        Args:
            filename: Input filename (UNSANITIZED!)
            output_format: Desired output format (UNVALIDATED!)
            input_folder: Folder containing input file
            output_folder: Folder for output file
        
        Returns:
            Dictionary with result information
        """
        # VULNERABILITY: NO INPUT SANITIZATION!
        input_path = os.path.join(input_folder, filename)
        output_filename = self._generate_output_filename(filename, output_format)
        output_path = os.path.join(output_folder, output_filename)

        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {filename}")
        
        # Get input file extension
        input_ext = os.path.splitext(filename)[1].lower()
        
        # Execute conversion (some methods are vulnerable to command injection!)
        success = self._execute_conversion(input_path, output_path, output_format, input_ext)

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
    
    def _execute_conversion(self, input_path, output_path, output_format, input_ext):
        """
        Execute the actual conversion command

        VULNERABILITY A03: Command Injection
        Some conversions use os.system() with user-controlled input:
        - Image to Image: os.system("cp ...") - VULNERABLE!
        - Text to Text: os.system("cat ... > ...") - VULNERABLE!
        - PDF to PDF: os.system("cp ...") - VULNERABLE!
        
        Safe conversions (use Python libraries):
        - Image to PDF: Pillow + ReportLab
        - Text to PDF: ReportLab

        Args:
            input_path: Full path to input file
            output_path: Full path to output file
            output_format: Target format
            input_ext: Input file extension
        
        Returns:
            Boolean indicating success
        """
        try:
            # Image to PDF - Safe (uses Pillow + ReportLab)
            if input_ext in self.image_extensions and output_format == 'pdf':
                return self._image_to_pdf(input_path, output_path)
            # Text to PDF - Safe (uses ReportLab)
            elif input_ext in self.text_extensions and output_format == 'pdf':
                return self._text_to_pdf(input_path, output_path)
            # Image to image - VULNERABLE! uses os.system() with user input which executes commands in a shell
            elif input_ext in self.image_extensions and output_format in ['png', 'jpg']:
                command = f"cp {input_path} {output_path}"
                result = os.system(command) # COMMAND INJECTION!
                return result == 0
            # Text to Text - VULNERABLE! Uses os.system() with user input
            elif input_ext in self.text_extensions and output_format == 'txt':
                command = f"cat {input_path} > {output_path}"
                result = os.system(command) # COMMAND INJECTION!
                return result == 0
            # PDF to PDF - VULNERABLE! Uses os.system() with user input
            elif input_ext == '.pdf' and output_format == 'pdf':
                command = f"cp {input_path} {output_path}"
                result = os.system(command) # COMMAND INJECTION
                return result == 0
            else:
                print(f"Unsupported conversion: {input_ext} to {output_format}")
                return False

        except Exception as e:
            print(f"Conversion error: {e}")
            return False
    
    def _image_to_pdf(self, input_path, output_path):
        """Convert image to PDF using Pillow and ReportLab"""
        try:
            img = Image.open(input_path)
            
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            img_width, img_height = img.size
            
            c = canvas.Canvas(output_path, pagesize=letter)
            page_width, page_height = letter
            
            margin = 0.5 * inch
            available_width = page_width - 2 * margin
            available_height = page_height - 2 * margin
            
            scale = min(available_width / img_width, available_height / img_height)
            new_width = img_width * scale
            new_height = img_height * scale
            
            x = (page_width - new_width) / 2
            y = (page_height - new_height) / 2
            
            temp_path = input_path + '.temp.jpg'
            img.save(temp_path, 'JPEG', quality=95)
            
            c.drawImage(temp_path, x, y, new_width, new_height)
            c.save()
            
            os.remove(temp_path)
            
            return True
        except Exception as e:
            print(f"Image to PDF error: {e}")
            return False
    
    def _text_to_pdf(self, input_path, output_path):
        """Convert text file to PDF using ReportLab"""
        try:
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.readlines()
            
            c = canvas.Canvas(output_path, pagesize=letter)
            page_width, page_height = letter
            
            c.setFont("Helvetica", 10)
            
            margin = 0.75 * inch
            y_position = page_height - margin
            line_height = 14
            
            for line in text_content:
                line = line.rstrip('\n\r')
                
                if y_position < margin:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y_position = page_height - margin
                
                max_chars = 90
                if len(line) > max_chars:
                    line = line[:max_chars] + "..."
                
                c.drawString(margin, y_position, line)
                y_position -= line_height
            
            c.save()
            return True
        except Exception as e:
            print(f"Text to PDF error: {e}")
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
        