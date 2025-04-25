from app import create_app
import os
from datetime import datetime

# Create necessary directories
os.makedirs('static/uploads/profile_images', exist_ok=True)
os.makedirs('static/documents', exist_ok=True)
os.makedirs('static/fonts', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

# Create the Flask app
app = create_app()

# Add template context processors
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Set configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['DOCUMENT_UPLOAD_PATH'] = 'static/documents'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'pdf'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
