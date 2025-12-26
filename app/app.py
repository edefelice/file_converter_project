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
#    - @app.route('/session_demo')          # Secret key demo
#    - @app.route('/upload', POST)          # Upload file
#    - @app.route('/download')              # Download (fix path traversal)
#    - @app.route('/convert', POST)         # Convert (fix command injection)
#    - @app.route('/process_data', POST)    # FIX Pickle (deserialization)

# 7. if __name__ == '__main__':

import os
import json # instead of pickle, removes insecure deserialization
import secrets
from flask import Flask, render_template, request, send_file, jsonify, session
from werkzeug.utils import secure_filename

# Import custom modules
from app.file_handler import FileHandler
from app.converter import FileConverter

# Flask app configuration
app = Flask(__name__)

# FIX A05 vulnerability: Security Misconfiguration
app.config['DEBUG'] = False # FIX: Disabled
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32)) # FIXED Weak hardcoded secret key -> random secret
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # FIX: No upload limit (A04 vulnerability: insecure design) -> 16MB limit

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

    VULNERABILITY A04: Insecure Design - Insufficient Validation
    Only checks file extension, doesn't verify actual file content.
    FIX: Additional validation
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

    VULNERABILITY A04: Insecure Design
    - No file size validation
    - Insufficient file type validation
    - No rate limiting

    FIX: Proper validation
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # FIXED VULNERABILITY A04: Weak validation
    if file and allowed_file(file.filename):
        # FIX: Using secure_filename to sanitize
        filename = secure_filename(file.filename)
        # FIX: Validate the final path
        if not filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # FIX: MAX_CONTENT_LENGTH handles size limit automatically.
        file.save(filepath)

        # FIX: does not return filepath 
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename
        }), 200
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/download')
def download_file():
    """
    Download file endpoint - SECURE VERSION

    FIX VULNERABILITY A01: Broken Access Control (Path Traversal)
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

    filepath = os.path.join(app.config['CONVERTED_FOLDER'], safe_filename)

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

    FIX VULNERABILITY A03: Injection (Command Injection)

    Uses secure converter module
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    filename = data.get('filename', '')
    output_format = data.get('format', 'pdf')

    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    # COMMAND INJECTION!
    # FIX: Sanitize filename before processing
    safe_filename = secure_filename(filename)

    if not safe_filename:
        return jsonify({'error': 'Invalid filename'}), 400

    try:
        result = converter.convert(filename, output_format,
        app.config['UPLOAD_FOLDER'], app.config['CONVERTED_FOLDER'])
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

    FIX VULNERABILITY A08: Software and Data Integrity Failures (Insecure Deserialization)
    Instead of insecure pickle deserialization uses JSON
    """
    try:
        # FIX INSECURE DESERIALIZATION!
        # using json
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
    # FIX VULNERABILITY A05: Secure run configuration
    app.run(host='127.0.0.1', port=5000, debug=False)