"""
Deepseek API client implementation
"""
import os
from typing import List, Dict, Union
import requests
from tenacity import retry, wait_exponential, stop_after_attempt

class DeepseekClient:
    """Client for interacting with Deepseek API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("Deepseek API key not provided")
            
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
        
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10),
           stop=stop_after_attempt(3))
    def get_embeddings(self, texts: Union[str, List[str]], 
                      model: str = "text-embedding-001") -> List[List[float]]:
        """Get embeddings for text(s)"""
        if isinstance(texts, str):
            texts = [texts]
            
        response = self.session.post(
            "https://api.deepseek.com/v1/embeddings",
            json={
                "input": texts,
                "model": model
            }
        )
        response.raise_for_status()
        
        return [item['embedding'] for item in response.json()['data']]
        
    def analyze_text(self, text: str, 
                    task: str = "summarize",
                    max_tokens: int = 500) -> Dict:
        """Analyze text using Deepseek's language models"""
        response = self.session.post(
            "https://api.deepseek.com/v1/chat/completions",
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"Perform {task} analysis on the following text."},
                    {"role": "user", "content": text}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        
        return {
            'task': task,
            'result': response.json()['choices'][0]['message']['content']
        } 