from PIL import Image
import base64
from io import BytesIO
from pathlib import Path

def load_image(path: str) -> Image.Image:
    """
    Load an image from a file path.
    
    Args:
        path: Path to the image file
        
    Returns:
        PIL Image object in RGB mode
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is not a valid image
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Image file not found: {path}")
    
    try:
        return Image.open(path).convert("RGB")
    except Exception as e:
        raise ValueError(f"Failed to load image from {path}: {e}") from e

def encode_image_to_base64(img: Image.Image) -> str:
    """
    Encode a PIL Image to base64 string.
    
    Args:
        img: PIL Image object
        
    Returns:
        Base64 encoded string of the image
        
    Raises:
        ValueError: If the image cannot be encoded
    """
    try:
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        raise ValueError(f"Failed to encode image to base64: {e}") from e
