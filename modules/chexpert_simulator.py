import random
from typing import List, Optional
from pathlib import Path

LABEL_POOL: List[str] = [
    "Cardiomegaly",
    "Pleural Effusion",
    "Pulmonary Edema",
    "Consolidation",
    "Atelectasis",
    "Pneumothorax",
    "Support Devices",
    "No Finding"
]

# Global MIMIC-CXR loader instance (lazy loaded)
_mimic_loader = None

def _get_mimic_loader():
    """Get or create MIMIC-CXR loader instance."""
    global _mimic_loader
    if _mimic_loader is None:
        try:
            from modules.mimic_cxr_loader import MIMICCXRLoader
            # Try to load from project root
            csv_path = Path(__file__).parent.parent / "mimic-cxr.csv"
            if csv_path.exists():
                _mimic_loader = MIMICCXRLoader(str(csv_path))
            else:
                # Try current directory
                csv_path = Path("mimic-cxr.csv")
                if csv_path.exists():
                    _mimic_loader = MIMICCXRLoader(str(csv_path))
        except Exception:
            # If loading fails, continue with simulation
            _mimic_loader = None
    return _mimic_loader

def simulate_chexpert_labels(image_path: str, use_mimic: bool = True) -> List[str]:
    """
    Get CheXpert labels for an image.
    
    First tries to load real labels from MIMIC-CXR dataset.
    Falls back to simulation if MIMIC-CXR data not available.
    
    Args:
        image_path: Path to the image file
        use_mimic: Whether to try loading from MIMIC-CXR dataset first
        
    Returns:
        List of CheXpert labels
    """
    # Try to use MIMIC-CXR dataset if available
    if use_mimic:
        loader = _get_mimic_loader()
        if loader:
            filename = Path(image_path).name
            labels = loader.get_labels(filename)
            if labels:
                return labels
    
    # Fall back to simulation
    filename = image_path.lower()

    if "cardio" in filename:
        return ["Cardiomegaly", "Pulmonary Edema"]
    elif "pleura" in filename:
        return ["Pleural Effusion"]
    elif "normal" in filename or "clear" in filename:
        return ["No Finding"]
    else:
        return random.sample(LABEL_POOL[:-1], k=random.randint(2, 4))
