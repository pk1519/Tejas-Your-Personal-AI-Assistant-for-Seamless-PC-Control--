"""
Model Manager for Tejas AI
Automatically scans and selects the best available speech recognition model
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for optional dependencies
try:
    import vosk
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logger.warning("Vosk not available - offline speech recognition disabled")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.warning("PyAudio not available - microphone access limited")

class ModelManager:
    """Manages speech recognition models with automatic scanning and selection"""
    
    def __init__(self, models_dir: Optional[str] = None):
        """
        Initialize ModelManager
        
        Args:
            models_dir: Directory to scan for models. Defaults to current directory.
        """
        self.models_dir = Path(models_dir) if models_dir else Path.cwd()
        self.models_cache_file = self.models_dir / "models_cache.json"
        self.available_models = {}
        self.selected_model = None
        self.model_config_cache = {}
        
        # Known model types and their characteristics
        self.model_types = {
            'vosk': {
                'extensions': ['.zip'],
                'config_files': ['conf/model.conf', 'README'],
                'priority': 90,
                'size_weight': 0.7,  # Larger models generally better
                'description': 'Offline speech recognition'
            },
            'whisper': {
                'extensions': ['.pt', '.bin'],
                'config_files': ['config.json'],
                'priority': 95,
                'size_weight': 0.8,
                'description': 'OpenAI Whisper model'
            },
            'wav2vec': {
                'extensions': ['.pt', '.bin'],
                'config_files': ['config.json', 'preprocessor_config.json'],
                'priority': 85,
                'size_weight': 0.6,
                'description': 'Facebook wav2vec2 model'
            },
            'deepspeech': {
                'extensions': ['.pbmm', '.pb'],
                'config_files': ['alphabet.txt'],
                'priority': 80,
                'size_weight': 0.5,
                'description': 'Mozilla DeepSpeech model'
            }
        }
        
    def scan_models(self, force_rescan: bool = False) -> Dict:
        """
        Scan directory for available speech recognition models
        
        Args:
            force_rescan: Force rescan even if cache exists
            
        Returns:
            Dictionary of discovered models
        """
        logger.info(f"Scanning for models in: {self.models_dir}")
        
        # Check cache first
        if not force_rescan and self._load_cache():
            logger.info(f"Loaded {len(self.available_models)} models from cache")
            return self.available_models
        
        self.available_models = {}
        
        try:
            # Scan for model files
            for model_type, config in self.model_types.items():
                models_found = self._scan_model_type(model_type, config)
                if models_found:
                    self.available_models.update(models_found)
            
            # Scan for extracted model directories
            self._scan_extracted_models()
            
            # Calculate model scores
            self._calculate_model_scores()
            
            # Save to cache
            self._save_cache()
            
            logger.info(f"Found {len(self.available_models)} models total")
            
        except Exception as e:
            logger.error(f"Error during model scanning: {e}")
            
        return self.available_models
    
    def _scan_model_type(self, model_type: str, config: Dict) -> Dict:
        """Scan for specific model type"""
        models = {}
        
        for extension in config['extensions']:
            pattern = f"*{extension}"
            for model_path in self.models_dir.rglob(pattern):
                if model_path.is_file():
                    model_info = self._analyze_model_file(model_path, model_type, config)
                    if model_info:
                        model_key = f"{model_type}_{model_path.stem}"
                        models[model_key] = model_info
                        
        return models
    
    def _scan_extracted_models(self):
        """Scan for extracted model directories"""
        for item in self.models_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if directory contains model files
                model_info = self._analyze_model_directory(item)
                if model_info:
                    model_key = f"extracted_{item.name}"
                    self.available_models[model_key] = model_info
    
    def _analyze_model_file(self, model_path: Path, model_type: str, config: Dict) -> Optional[Dict]:
        """Analyze a model file and extract information"""
        try:
            file_size = model_path.stat().st_size
            file_hash = self._get_file_hash(model_path)
            
            model_info = {
                'path': str(model_path),
                'type': model_type,
                'size': file_size,
                'hash': file_hash,
                'priority': config['priority'],
                'description': config['description'],
                'is_extracted': False,
                'config_files': [],
                'score': 0  # Will be calculated later
            }
            
            # Check for associated config files
            model_dir = model_path.parent
            for config_file in config.get('config_files', []):
                config_path = model_dir / config_file
                if config_path.exists():
                    model_info['config_files'].append(str(config_path))
            
            return model_info
            
        except Exception as e:
            logger.error(f"Error analyzing model file {model_path}: {e}")
            return None
    
    def _analyze_model_directory(self, model_dir: Path) -> Optional[Dict]:
        """Analyze a model directory"""
        try:
            # Check for known model indicators
            model_type = None
            config_files = []
            
            # Look for Vosk model indicators
            if (model_dir / 'conf' / 'model.conf').exists():
                model_type = 'vosk'
                config_files.append(str(model_dir / 'conf' / 'model.conf'))
                
            # Look for other model types
            if not model_type:
                for file in model_dir.iterdir():
                    if file.name == 'config.json':
                        model_type = 'whisper'  # Could be whisper or wav2vec
                        config_files.append(str(file))
                        break
            
            if not model_type:
                return None
            
            # Calculate directory size
            total_size = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
            
            model_info = {
                'path': str(model_dir),
                'type': model_type,
                'size': total_size,
                'hash': self._get_directory_hash(model_dir),
                'priority': self.model_types[model_type]['priority'],
                'description': self.model_types[model_type]['description'],
                'is_extracted': True,
                'config_files': config_files,
                'score': 0
            }
            
            # Try to extract additional info from config files
            self._extract_model_metadata(model_info, model_dir)
            
            return model_info
            
        except Exception as e:
            logger.error(f"Error analyzing model directory {model_dir}: {e}")
            return None
    
    def _extract_model_metadata(self, model_info: Dict, model_dir: Path):
        """Extract metadata from model configuration files"""
        try:
            # For Vosk models
            if model_info['type'] == 'vosk':
                readme_path = model_dir / 'README'
                if readme_path.exists():
                    readme_content = readme_path.read_text(encoding='utf-8', errors='ignore')
                    # Extract accuracy info
                    for line in readme_content.split('\n'):
                        if 'Accuracy:' in line:
                            model_info['accuracy'] = line.split('Accuracy:')[1].strip()
                        elif 'Speed:' in line:
                            model_info['speed'] = line.split('Speed:')[1].strip()
                        elif 'language' in line.lower() or 'english' in line.lower():
                            model_info['language'] = 'en-US'
            
            # For other model types, try to read config.json
            config_path = model_dir / 'config.json'
            if config_path.exists():
                try:
                    config = json.loads(config_path.read_text())
                    model_info['config'] = config
                except:
                    pass
                    
        except Exception as e:
            logger.warning(f"Could not extract metadata for {model_dir}: {e}")
    
    def _calculate_model_scores(self):
        """Calculate scores for all models to determine the best one"""
        if not self.available_models:
            return
        
        # Find size statistics for normalization
        sizes = [model['size'] for model in self.available_models.values()]
        max_size = max(sizes) if sizes else 1
        
        for model_key, model_info in self.available_models.items():
            score = 0
            
            # Base priority score (0-100)
            score += model_info['priority']
            
            # Size bonus (larger models often better, but with diminishing returns)
            size_ratio = model_info['size'] / max_size
            size_weight = self.model_types[model_info['type']]['size_weight']
            score += size_ratio * size_weight * 20
            
            # Bonus for extracted models (ready to use)
            if model_info['is_extracted']:
                score += 15
            
            # Bonus for having config files
            if model_info['config_files']:
                score += len(model_info['config_files']) * 5
            
            # Language preference (English models get bonus)
            if 'language' in model_info and 'en' in model_info['language'].lower():
                score += 10
            
            # Accuracy bonus (if available)
            if 'accuracy' in model_info:
                try:
                    # Extract numeric accuracy value
                    acc_str = model_info['accuracy'].split()[0]
                    accuracy = float(acc_str)
                    # Lower WER is better, so invert
                    if accuracy < 20:  # Reasonable WER range
                        score += (20 - accuracy) * 2
                except:
                    pass
            
            model_info['score'] = score
    
    def select_best_model(self) -> Optional[Dict]:
        """Select the best available model based on scores"""
        if not self.available_models:
            logger.warning("No models available for selection")
            return None
        
        # Sort by score (highest first)
        sorted_models = sorted(
            self.available_models.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        if sorted_models:
            best_model_key, best_model = sorted_models[0]
            self.selected_model = best_model
            
            logger.info(f"Selected best model: {best_model_key}")
            logger.info(f"  Type: {best_model['type']}")
            logger.info(f"  Path: {best_model['path']}")
            logger.info(f"  Size: {self._format_size(best_model['size'])}")
            logger.info(f"  Score: {best_model['score']:.1f}")
            
            return best_model
        
        return None
    
    def get_model_info(self) -> Dict:
        """Get information about all discovered models"""
        return {
            'total_models': len(self.available_models),
            'selected_model': self.selected_model,
            'models': self.available_models
        }
    
    def get_selected_model_path(self) -> Optional[str]:
        """Get the path to the selected model"""
        if self.selected_model:
            return self.selected_model['path']
        return None
    
    def _get_file_hash(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Calculate MD5 hash of a file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return "unknown"
    
    def _get_directory_hash(self, dir_path: Path) -> str:
        """Calculate hash of a directory based on its contents"""
        try:
            hash_md5 = hashlib.md5()
            for file_path in sorted(dir_path.rglob('*')):
                if file_path.is_file():
                    hash_md5.update(str(file_path.relative_to(dir_path)).encode())
                    hash_md5.update(str(file_path.stat().st_size).encode())
            return hash_md5.hexdigest()
        except:
            return "unknown"
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _load_cache(self) -> bool:
        """Load models from cache file"""
        try:
            if self.models_cache_file.exists():
                cache_data = json.loads(self.models_cache_file.read_text())
                self.available_models = cache_data.get('models', {})
                self.selected_model = cache_data.get('selected_model')
                return len(self.available_models) > 0
        except Exception as e:
            logger.warning(f"Could not load cache: {e}")
        return False
    
    def _save_cache(self):
        """Save models to cache file"""
        try:
            cache_data = {
                'models': self.available_models,
                'selected_model': self.selected_model,
                'scan_time': str(Path.cwd())  # Simple cache invalidation
            }
            self.models_cache_file.write_text(json.dumps(cache_data, indent=2))
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")


# Convenience functions for easy integration
def scan_and_select_model(models_dir: Optional[str] = None) -> Optional[Dict]:
    """Convenience function to scan and select the best model"""
    manager = ModelManager(models_dir)
    manager.scan_models()
    return manager.select_best_model()

def get_best_model_path(models_dir: Optional[str] = None) -> Optional[str]:
    """Get path to the best available model"""
    model = scan_and_select_model(models_dir)
    return model['path'] if model else None

# Example usage and testing
if __name__ == "__main__":
    # Test the model manager
    manager = ModelManager()
    models = manager.scan_models()
    
    print(f"Found {len(models)} models:")
    for key, model in models.items():
        print(f"  {key}: {model['type']} - {manager._format_size(model['size'])} - Score: {model['score']:.1f}")
    
    best_model = manager.select_best_model()
    if best_model:
        print(f"\nBest model: {best_model['path']}")
    else:
        print("\nNo suitable model found")