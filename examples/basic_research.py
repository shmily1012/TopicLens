"""
Example script demonstrating basic research workflow
"""
import os
from dotenv import load_dotenv
from research_engine.config import load_config
from research_engine.data_collector import DataCollector
from research_engine.deepseek_client import DeepseekClient

def main():
    # Load environment variables and config
    load_dotenv()
    config = load_config()
    
    # Initialize components
    collector = DataCollector(config)
    deepseek = DeepseekClient()
    
    # Collect data
    query = "Latest developments in quantum computing"
    results = collector.collect_data(query, sources=['google'])
    
    # Get embeddings and analyze
    texts = [r['snippet'] for r in results if r['snippet']]
    embeddings = deepseek.get_embeddings(texts)
    
    # Analyze first result as example
    if texts:
        analysis = deepseek.analyze_text(
            texts[0], 
            task="Summarize the key points and technical details"
        )
        print(f"Analysis result:\n{analysis['result']}")

if __name__ == "__main__":
    main() 