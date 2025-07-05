import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class FeatureExtractor:
    def __init__(self, model_type='resnet50', target_dim=2048):
        self.target_dim = target_dim
        self.model_type = model_type
        self.device = torch.device('cpu')  # Use CPU for deployment
        
        # Load model
        if model_type == 'resnet50':
            base_model = models.resnet50(pretrained=True)
            self.model = nn.Sequential(*list(base_model.children())[:-1])
            self.native_dim = 2048
        
        self.model.eval()
        self.model.to(self.device)
        
        # Preprocessing
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406], 
                std=[0.229, 0.224, 0.225]
            ),
        ])
        
        logger.info(f"Initialized {model_type} feature extractor")
    
    def extract(self, image):
        """Extract features from PIL Image"""
        try:
            # Transform image
            logger.info("Transforming image...")
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Extract features
            with torch.no_grad():
                features = self.model(image_tensor)
                features = features.view(features.size(0), -1)
                features = features.cpu().numpy().flatten()
            
            # Normalize
            logger.info("Normalizing vector...")
            norm = np.linalg.norm(features)
            if norm > 0:
                features = features / norm
            
            # Pad or truncate
            if len(features) < self.target_dim:
                padded = np.zeros(self.target_dim)
                padded[:len(features)] = features
                features = padded
            elif len(features) > self.target_dim:
                features = features[:self.target_dim]
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            raise