import os
from pinecone import Pinecone
import logging

logger = logging.getLogger(__name__)

class PineconeClient:
    def __init__(self, index_name, project_name):
        self.project_name = project_name
        
        # Initialize Pinecone
        api_key = os.environ.get('PINECONE_API_KEY')
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        
        pc = Pinecone(
            api_key=api_key
        )

        if not pc.has_index(index_name):
            raise ValueError(f"Pinecone index '{index_name}' does not exist")
        
        self.index = pc.Index(index_name)
        logger.info(f"Connected to Pinecone index: {index_name}")
    
    def search(self, features, category_filter=None, top_k=10):
        """Search for similar images"""
        # Build filter
        filter_dict = {"project": {"$eq": self.project_name}}
        if category_filter:
            filter_dict["category"] = {"$eq": category_filter}
        
        # Query
        results = self.index.query(
            vector=features.tolist(),
            top_k=top_k,
            include_metadata=True,
            namespace=self.project_name,
            filter=filter_dict
        )
        
        return results['matches']
    
    def get_stats(self):
        """Get index statistics"""
        stats = self.index.describe_index_stats()
        
        namespace_stats = {}
        if stats.namespaces:
            for ns, data in stats.namespaces.items():
                namespace_stats[ns] = data['vector_count']
        
        return {
            'total_vectors': stats.total_vector_count,
            'dimension': stats.dimension,
            'namespaces': namespace_stats,
            'current_project': self.project_name,
            'free_tier_usage': f"{stats.total_vector_count/100000*100:.1f}%"
        }
    
    def keep_alive(self):
        """Keep index active to prevent archiving"""
        return self.get_stats()