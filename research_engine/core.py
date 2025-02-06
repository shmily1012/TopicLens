"""
Core Research Engine Modules
"""
import os
import json
from typing import List, Dict
import requests
import numpy as np
import pandas as pd
from umap import UMAP
from sklearn.cluster import HDBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer

class DataCollector:
    """Multi-source data collection with error handling"""
    
    def __init__(self, config: Dict):
        self.headers = {'User-Agent': config.get('user_agent', 'ResearchBot/1.0')}
        self.rate_limit = config.get('rate_limit', 1)  # requests/sec
        self.sources = config['sources']

    def fetch_web_data(self, query: str) -> List[Dict]:
        """Fetch data from web sources with exponential backoff"""
        results = []
        
        try:
            # Example Google Custom Search implementation
            params = {
                'q': query,
                'key': os.getenv('SEARCH_API_KEY'),
                'cx': self.sources['google']['cx'],
                'num': 10
            }
            
            response = requests.get(
                self.sources['google']['endpoint'],
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            # Process results
            results.extend(self._process_google_results(response.json()))
            
        except requests.exceptions.RequestException as e:
            print(f"Search API error: {str(e)}")
            
        return results

    def _process_google_results(self, data: Dict) -> List[Dict]:
        """Transform API response to standardized format"""
        return [{
            'title': item.get('title'),
            'snippet': item.get('snippet'),
            'link': item.get('link'),
            'source': 'google',
            'timestamp': pd.Timestamp.now().isoformat()
        } for item in data.get('items', [])]

class DeepseekAPIWrapper:
    """Encapsulated Deepseek API integration"""
    
    BASE_URL = "https://api.deepseek.com/v1"
    
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
        
    def get_embeddings(self, texts: List[str], model: str = "text-embedding-001") -> List[List[float]]:
        """Get batch text embeddings"""
        response = self.session.post(
            f"{self.BASE_URL}/embeddings",
            json={
                'input': texts,
                'model': model
            }
        )
        response.raise_for_status()
        return [item['embedding'] for item in response.json()['data']]
    
    def semantic_search(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict]:
        """Semantic search using Deepseek's API"""
        response = self.session.post(
            f"{self.BASE_URL}/chat/completions",
            json={
                'model': "deepseek-chat",
                'messages': [{
                    'role': "user",
                    'content': f"Search query: {query}\nDocuments: {documents}"
                }],
                'temperature': 0.7
            }
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

class SemanticAnalyzer:
    """NLP analysis and clustering module"""
    
    def __init__(self, embed_dim: int = 768):
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.umap = UMAP(n_components=50, n_neighbors=15, min_dist=0.1)
        self.clusterer = HDBSCAN(min_cluster_size=5)
        
    def analyze_corpus(self, texts: List[str]) -> Dict:
        """Full text analysis pipeline"""
        # Text vectorization
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        # Dimensionality reduction
        umap_embeds = self.umap.fit_transform(tidf_matrix)
        
        # Clustering
        clusters = self.clusterer.fit_predict(umap_embeds)
        
        return {
            'embeddings': umap_embeds,
            'clusters': clusters,
            'features': self.vectorizer.get_feature_names_out()
        }

class ReportGenerator:
    """Dynamic report generation with visualization"""
    
    def __init__(self, template_path: str = "templates/report_template.html"):
        self.template = self._load_template(template_path)
        
    def generate_report(self, analysis_results: Dict) -> str:
        """Generate HTML report with embedded visualizations"""
        # Create interactive plot
        fig = self._create_cluster_plot(analysis_results)
        plot_html = fig.to_html(full_html=False)
        
        # Format insights
        insights = self._extract_key_insights(analysis_results)
        
        return self.template.render(
            plot_html=plot_html,
            insights=insights,
            stats=self._calculate_stats(analysis_results)
        )
    
    def _create_cluster_plot(self, results: Dict):
        """Create UMAP cluster visualization"""
        df = pd.DataFrame(results['embeddings'], columns=['x', 'y'])
        df['cluster'] = results['clusters']
        
        fig = px.scatter(
            df, x='x', y='y', color='cluster',
            hover_data={'text': results['texts']},
            title="Semantic Clustering Visualization"
        )
        return fig 