"""
File Converter Application - Main Flask App
Branch: insecure (educational)

WARNING: This code contains intentional vulnerabilites for educational purposes.
Do NOT use in production!
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
#    - @app.route('/download')              # Download (path traversal)
#    - @app.route('/convert', POST)         # Convert (command injection)
#    - @app.route('/process_data', POST)    # Pickle (deserialization)

# 7. if __name__ == '__main__':

import os
import pickle # for insecure deserialization (A08 vulnerability)
from flask import Flask, render_template, request, send_file, jsonify, session
from werkzeug.utils import secure_filename

# Import custom modules
from file_handler import FileHandler
from converter import FileConverter

# Flask app configuration
app = Flask(__name__)

# A05 vulnerability: Security Misconfiguration
app.config['DEBUG'] = True # Exposes sensitive info
app.config['SECRET_KEY'] = 'dev-secret-key-123' # Weak hardcoded secret key
app.config['MAX_CONTENT_LENGTH'] = None # No upload limit (A04 vulnerability: insecure design)

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
    Attacker can bypass by renaming malicious files (e.g. malware.exe.pdf)
    """
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#=========================
# ROUTES
#=========================

@app.route('/')
def index():
    """
    Homepage with file upload form
    """
    return render_template('index.html')

@app.route('/session_demo')
def session_demo():
    """
    VULNERABILITY A05: Demonstrates weak SECRET_KEY usage

    The hardcoded SECRET_KEY can be discovered from source code,
    allowing attackers to forge session cookies.
    """

    # Store sensitive data in session (signed with weak SECRET_KEY)
    session['user_role'] = 'admin'
    session['sensitive_data'] = 'confidential_information'

    return jsonify({
        'message': 'Session data set with weak SECRET_KEY',
        'secret_key': app.config['SECRET_KEY'], # Exposes secret key!
        'session_data': dict(session)
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    File upload endpoint

    VULNERABILITY A04: Insecure Design
    - No file size validation
    - Insufficient file type validation
    - No rate limiting
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # VULNERABILITY A04: Weak validation - only checks extension
    if file and allowed_file(file.filename):
        # Using secure_filename but still vulnerable to other attacks
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # No file size check before saving (MAX_CONTENT_LENGTH is None)
        file.save(filepath)

        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'path': filepath
        }), 200
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/download')
def download_file():
    """
    Download file endpoint

    VULNERABILITY A01: Broken Access Control (Path Traversal)

    Allows attackers to download ANY file on the system by manipulating the filename parameter.
    Example: /download?filename=../../etc/passwd
    """
    filename = request.args.get('filename', '')

    # NO PATH VALIDATION!
    # Attacker can use ../ to access files outside the intended directory
    filepath = os.path.join(app.config['CONVERTED_FOLDER'], filename)

    # No check if file exists or if path is safe
    try:
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        # Exposing error details (A05: Security Misconfiguration)
        return jsonify({'error': str(e)}), 404

@app.route('/convert', methods=['POST'])
def convert_file():
    """
    File converstion endpoint

    VULNERABILITY A03: Injection (Command Injection)

    User input is passed directly to system commands without sanitization.
    Attacker can execute arbitrary system commands.
    """
    data = request.get_json()
    filename = data.get('filename', '')
    output_format = data.get('format', 'pdf')

    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    # COMMAND INJECTION!
    # Uses the converter module which will execute unsanitized shell commands
    try:
        result = converter.convert(filename, output_format,
        app.config['UPLOAD_FOLDER'], app.config['CONVERTED_FOLDER'])
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process_data', methods=['POST'])
def process_data():
    """
    Data processing endpoint

    VULNERABILITY A08: Software and Data Integrity Failures (Insecure Deserialization)

    Deserializes user-provided data using pickle, which can execute arbitrary code.
    """
    try:
        # INSECURE DESERIALIZATION!
        # pickle.loads() can execute arbitrary code if data is malicious
        user_data = request.data
        obj = pickle.loads(user_data)

        return jsonify({
            'message': 'Data processed',
            'data': str(obj)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Run the application
if __name__ == '__main__':
    # VULNERABILITY A05: Running with debug=True and host='0.0.0.0' in production
    app.run(host='0.0.0.0', port=5000, debug=True)