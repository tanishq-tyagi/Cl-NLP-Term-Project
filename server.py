from flask import Flask, request, jsonify, send_from_directory
import os
import subprocess
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define directories
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
INTERMEDIATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "intermediate")

# Ensure the directories exist
for directory in [UPLOADS_DIR, OUTPUT_DIR, INTERMEDIATE_DIR]:
    os.makedirs(directory, exist_ok=True)

@app.route('/api/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return jsonify({"error": "No files provided"}), 400
    
    files = request.files.getlist('files[]')
    
    if not files:
        return jsonify({"error": "No files selected"}), 400
    
    for file in files:
        if file.filename:
            file.save(os.path.join(UPLOADS_DIR, file.filename))
    
    return jsonify({"message": f"Successfully uploaded {len(files)} files"}), 200

@app.route('/api/process', methods=['POST'])
def process_files():
    try:
        # Run the main.py script
        subprocess.run(['python', 'main.py'], check=True)
        
        # Get the output file - ensure we get the most recently created file
        output_files = [f for f in os.listdir(OUTPUT_DIR) if os.path.isfile(os.path.join(OUTPUT_DIR, f))]
        
        if not output_files:
            return jsonify({"error": "No output files generated"}), 500
        
        # Sort files by creation time (newest first)
        output_files.sort(key=lambda f: os.path.getmtime(os.path.join(OUTPUT_DIR, f)), reverse=True)
        latest_file = output_files[0]
        
        return jsonify({"message": "Processing complete", "filename": latest_file}), 200
    
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

@app.route('/api/files', methods=['GET'])
def get_files():
    output_files = [f for f in os.listdir(OUTPUT_DIR) if os.path.isfile(os.path.join(OUTPUT_DIR, f))]
    return jsonify({"files": output_files})

if __name__ == '__main__':
    app.run(debug=True, port=5000)