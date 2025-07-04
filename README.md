# Visual Search

AI-powered visual search for animal faces using the AFHQ dataset.

## Features

- Search for similar cats, dogs, and wild animals
- Category filtering
- Drag-and-drop image upload
- Real-time similarity scoring
- Support multi-project on Pinecone free plan

## Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env

# Run the app
python app.py