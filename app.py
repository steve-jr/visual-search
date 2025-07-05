import os
import io
import base64
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from PIL import Image
import numpy as np
from utils.feature_extractor import FeatureExtractor
from utils.pinecone_client import PineconeClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
COMMON_DIMENSION = 2048
PROJECT_NAME = "visual-search"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Initialize services
try:
    feature_extractor = FeatureExtractor(
        model_type='resnet50', 
        target_dim=COMMON_DIMENSION
    )
    pinecone_client = PineconeClient(
        index_name="multi-project-index",
        project_name=PROJECT_NAME
    )
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "project": PROJECT_NAME,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/search', methods=['POST'])
def search():
    """Handle image search requests"""
    try:
        # Validate request
        if 'image' not in request.json:
            return jsonify({'error': 'No image provided'}), 400
        
        # Validate image
        image_data = request.json['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        if len(image_bytes) > MAX_FILE_SIZE:
            return jsonify({'error': 'Image too large (max 10MB)'}), 400
        
    
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')

        category_filter = request.json.get('category', 'all')
        top_k = min(request.json.get('top_k', 10), 20)  # Max 20 results
        
        # Extract features
        logger.info("Extracting features...")
        features = feature_extractor.extract(image)
        
        # Search in Pinecone
        logger.info(f"Searching with filter: {category_filter}")
        results = pinecone_client.search(
            features=features,
            category_filter=category_filter if category_filter != 'all' else None,
            top_k=top_k
        )
        
        # Format results
        formatted_results = []
        
        for match in results:
            formatted_results.append({
                'id': match['id'],
                'score': float(match['score']),
                'category': match['metadata'].get('category', 'unknown'),
                'filename': match['metadata'].get('filename', 'unknown'),
                'image_url': match['metadata'].get('image_url', 'unknown')
            })
        
        return jsonify({
            'status': 'success',
            'results': formatted_results,
            'count': len(formatted_results)
        })
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred during search'
        }), 500

@app.route('/api/stats')
def stats():
    """Get index statistics"""
    try:
        stats = pinecone_client.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({'error': 'Failed to get stats'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)