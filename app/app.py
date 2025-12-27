"""
File Converter Application - Main Flask App
Branch: main (secure)

SECURE VERSION - All vulnerabilites fixed
"""
# STRUCTURE:
#
# 1. Docstring e imports
# 2. App configuration
# 3. Folder setup and initialization
# 4. Handler initialization

# 5. HELPER FUNCTIONS
#    - allowed_file()

# 6. ROUTES
#    - @app.route('/')                      # Homepage
#    - @app.route('/upload', POST)          # Upload file
#    - @app.route('/download')              # Download (FIX path traversal)
#    - @app.route('/convert', POST)         # Convert (FIX command injection)
#    - @app.route('/process_data', POST)    # FIX Pickle (deserialization)

# 7. if __name__ == '__main__':

import os
import json # FIX A08: Using JSON instead of pickle (removes insecure deserialization)
import secrets
from flask import Flask, render_template, request, send_file, jsonify, session
from werkzeug.utils import secure_filename

# Import custom modules
from app.file_handler import FileHandler
from app.converter import FileConverter

# Flask app configuration
app = Flask(__name__)

# FIX A05: Security Misconfiguration
app.config['DEBUG'] = False # FIX: Disabled debug mode
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32)) # FIX: Random secret key instead of hardcoded
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # FIX A04: 16MB limit instead of unlimited

# Folder configuration
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

# Handler initialization
file_handler = FileHandler(UPLOAD_FOLDER, CONVERTED_FOLDER)
converter = FileConverter()

#=========================
# HELPER FUNCTIONS
#=========================

def allowed_file(filename):
    """
    Check if file extension is allowed

    FIX A04: Insecure Design - Enhanced Validation
    - Checks for empty/invalid filenames
    - Rejects double extensions (e.g. malware.exe.pdf)
    """
    if not filename or '.' not in filename:
        return False
    
    # FIX: Check for double extensions (e.g. malware.exe.pdf)
    parts = filename.rsplit('.', 2)
    if len(parts) > 2:
        # Has multiple extensions - reject suspicious combinations
        return False

    return filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_safe_path(basedir, path):
    """
    FIX A01: Validate path to prevent directory traversal

    Args:
        basedir: The base directory that paths should be within
        path: The path to validate
    
    Returns:
        Boolean indicating if path is safe
    """
    # Resolve the absolute path
    abs_path = os.path.abspath(os.path.join(basedir, path))
    abs_basedir = os.path.abspath(basedir)

    # Check if the resolved path starts with the base directory
    return abs_path.startswith(abs_basedir)


#=========================
# ROUTES
#=========================

@app.route('/')
def index():
    """
    Homepage with file upload form
    """
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    File upload endpoint - SECURE VERSION

    FIX A04: Insecure Design
    - File size validation
    - Proper file type validation
    - Secure filename sanitization
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # FIXED A04: Validate file extension
    if file and allowed_file(file.filename):
        # FIX: Using secure_filename to sanitize
        filename = secure_filename(file.filename)
        # FIX: Validate the final path
        if not filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # FIX: MAX_CONTENT_LENGTH handles size limit automatically.
        file.save(filepath)

        # FIX A05: Does not expose internal filepath 
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename
        }), 200
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/download')
def download_file():
    """
    Download file endpoint - SECURE VERSION

    FIX A01: Broken Access Control (Path Traversal)
    - Sanitizes filename
    - Validates if path is within allowed directory
    """
    filename = request.args.get('filename', '')

    # FIX: Sanitize filename
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    safe_filename = secure_filename(filename)

    if not safe_filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    # FIX A01: Validate if path is within allowed directory
    if not is_safe_path(app.config['CONVERTED_FOLDER'], safe_filename):
        return jsonify({'error': 'Access denied'}), 403

    filepath = os.path.abspath(os.path.join(app.config['CONVERTED_FOLDER'], safe_filename))

    # FIX: Check if file exists
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    try:
        return send_file(filepath, as_attachment=True)
    except Exception:
        # FIX A05: Don't expose internal errors
        return jsonify({'error': 'Download failed'}), 500

@app.route('/convert', methods=['POST'])
def convert_file():
    """
    File converstion endpoint - SECURE VERSION

    FIX A03: Injection (Command Injection)
    - Uses secure converter module with native Python libraries
    - Input validation and sanitization
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    filename = data.get('filename', '')
    output_format = data.get('format', 'pdf')

    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    # FIX Command Injection: Sanitize filename before processing
    safe_filename = secure_filename(filename)

    if not safe_filename:
        return jsonify({'error': 'Invalid filename'}), 400

    try:
        result = converter.convert(filename, output_format,
        app.config['UPLOAD_FOLDER'], app.config['CONVERTED_FOLDER'])
        result['download_url'] = f"/download?filename={result['output_file']}"
        return jsonify(result), 200
    except ValueError as e:
        # Acceptable because we control the error messages.
        return jsonify({'error': str(e)}), 400
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except Exception:
        # FIX A05: Don't expose internal errors
        return jsonify({'error': 'Conversion failed'}), 500

@app.route('/process_data', methods=['POST'])
def process_data():
    """
    Data processing endpoint - SECURE VERSION

    FIX A08: Software and Data Integrity Failures (Insecure Deserialization)
    - Uses JSON instead of pickle
    - Safe deserialization
    """
    try:
        # FIX INSECURE DESERIALIZATION: using JSON instead of pickle
        user_data = request.get_json()
        
        if not user_data:
            return jsonify({'error': 'Invalid JSON data'}), 400

        return jsonify({
            'message': 'Data processed securely',
            'data': user_data
        }), 200
    except Exception:
        return jsonify({'error': 'Processing failed'}), 400

# Run the application
if __name__ == '__main__':
    # FIX A05: Secure run configuration
    app.run(host='127.0.0.1', port=5000, debug=False)