"""
Configuration and environment management
"""
import os
from pathlib import Path
import yaml

def load_config(config_path: str = "config/config.yaml") -> Dict:
    """Load YAML configuration with environment variables"""
    with open(config_path) as f:
        config = yaml.safe_load(f)
        
    # Replace environment variables
    for section in ['api_keys', 'paths']:
        if section in config:
            for key, value in config[section].items():
                if isinstance(value, str) and value.startswith('${'):
                    env_var = value[2:-1]
                    config[section][key] = os.getenv(env_var)
                    
    return config

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" 