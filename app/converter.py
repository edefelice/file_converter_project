"""
File Converter Module
Handles file format conversions

Branch: main (secure)
Contains COMMAND INJECTION vulnerability (A03) FIXED
"""

import os
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

class FileConverter:
    """
    Handles file conversions - SECURE VERSION

    FIX A03: Command Injection
    - Removed os.system() calls that were vulnerable to injection
    - All conversions now use safe Python methods (Pillow, file I/O)
    """

    def __init__(self):
        """ Initialize the converter"""
        self.supported_formats = ['pdf', 'txt', 'png', 'jpg']
        self.image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
        self.text_extensions = {'.txt', '.md', '.csv'}
    
    def convert(self, filename, output_format, input_folder, output_folder):
        """
        Convert file to specified format - SECURE VERSION

        FIX A03: COMMAND INJECTION
        - Added input validation (whitelist, path traversal check)
        - uses os.path.basename() for safe filename handling
        
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
        
        # Get input file extension
        input_ext = os.path.splitext(safe_filename)[1].lower()

        # FIX Command Injection: All conversions use safe Python methods (no shell commands)
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
        Execute the actual conversion command - SECURE VERSION

        FIX A03 - Command Injection
        INSECURE version used os.system() for image-to-image, text-to-text, pdf-to-pdf:
            command = f"cp {input_path} {output_path}"  # VULNERABLE!
            os.system(command)
        
        SECURE version uses:
        - Pillow for image conversions (_image_to_image)
        - Python file I/O for copies (_copy_file)
        - No shell commands = No injection possible

        Args:
            input_path: Full path to input file
            output_path: Full path to output file
            output_format: Target format
            input_ext: File extension of input file
        
        Returns:
            Boolean indicating success
        """
        try:
            # FIX Command Injection

            # Image to PDF (uses Pillow + ReportLab)
            if input_ext in self.image_extensions and output_format == 'pdf':
                return self._image_to_pdf(input_path, output_path)
            # Text to PDF (uses ReportLab)
            elif input_ext in self.text_extensions and output_format == 'pdf':
                return self._text_to_pdf(input_path, output_path)
            # Image to Image (format conversion) - FIX: uses Pillow instead of os.system("cp ...")
            elif input_ext in self.image_extensions and output_format in ['png', 'jpg']:
                return self._image_to_image(input_path, output_path, output_format)
            # Text to Text - FIX: uses Python I/O instead of os.system("cat ... > ...")
            elif input_ext in self.text_extensions and output_format == 'txt':
                return self._copy_file(input_path, output_path)
            # PDF to PDF - FIX: uses Python I/O instead of os.system("cp ...")
            elif input_ext == '.pdf' and output_format == 'pdf':
                return self._copy_file(input_path, output_path)
            # Unsupported conversion
            else:
                print(f"Unsupported conversion: {input_ext} to {output_format}")
                return False
            
        except Exception as e:
            print(f"Conversion error: {e}")
            return False

    def _image_to_pdf(self, input_path, output_path):
        """Convert image to PDF using Pillow and ReportLab"""
        try:
            # Open image with Pillow
            img = Image.open(input_path)
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Get image dimensions
            img_width, img_height = img.size
            
            # Create PDF with ReportLab
            c = canvas.Canvas(output_path, pagesize=letter)
            page_width, page_height = letter
            
            # Calculate scaling to fit page (with margins)
            margin = 0.5 * inch
            available_width = page_width - 2 * margin
            available_height = page_height - 2 * margin
            
            # Scale image to fit
            scale = min(available_width / img_width, available_height / img_height)
            new_width = img_width * scale
            new_height = img_height * scale
            
            # Center image on page
            x = (page_width - new_width) / 2
            y = (page_height - new_height) / 2
            
            # Save image temporarily for ReportLab
            temp_path = input_path + '.temp.jpg'
            img.save(temp_path, 'JPEG', quality=95)
            
            # Draw image on PDF
            c.drawImage(temp_path, x, y, new_width, new_height)
            c.save()
            
            # Clean up temp file
            os.remove(temp_path)
            
            return True
        except Exception as e:
            print(f"Image to PDF error: {e}")
            return False
    
    def _text_to_pdf(self, input_path, output_path):
        """Convert text file to PDF using ReportLab"""
        try:
            # Read text content
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.readlines()
            
            # Create PDF
            c = canvas.Canvas(output_path, pagesize=letter)
            page_width, page_height = letter
            
            # Set font
            c.setFont("Helvetica", 10)
            
            # Starting position
            margin = 0.75 * inch
            y_position = page_height - margin
            line_height = 14
            
            for line in text_content:
                # Remove newline and handle long lines
                line = line.rstrip('\n\r')
                
                # Check if we need a new page
                if y_position < margin:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y_position = page_height - margin
                
                # Draw text (truncate if too long)
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
    
    def _image_to_image(self, input_path, output_path, output_format):
        """
        Convert image to another image format using Pillow
        
        FIX A03: Replaces vulnerable os.system("cp ...") from insecure version
        """
        try:
            img = Image.open(input_path)
            
            # Convert to RGB for JPEG (doesn't support transparency)
            if output_format == 'jpg' and img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Save in new format
            if output_format == 'jpg':
                img.save(output_path, 'JPEG', quality=95)
            else:
                img.save(output_path, output_format.upper())
            
            return True
        except Exception as e:
            print(f"Image to image error: {e}")
            return False
    
    def _copy_file(self, input_path, output_path):
        """
        Copy file (for same-format conversions) using Python I/O
        
        FIX A03: Replaces vulnerable os.system("cp/cat ...") from insecure version
        """
        try:
            with open(input_path, 'rb') as src:
                with open(output_path, 'wb') as dst:
                    dst.write(src.read())
            return True
        except Exception as e:
            print(f"Copy file error: {e}")
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
        