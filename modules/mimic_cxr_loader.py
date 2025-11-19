"""
MIMIC-CXR Dataset Loader
Loads real CheXpert labels from mimic-cxr.csv for validation.
"""
import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path


class MIMICCXRLoader:
    """
    Loads and queries CheXpert labels from MIMIC-CXR dataset CSV file.
    """
    
    def __init__(self, csv_path: str = "mimic-cxr.csv"):
        """
        Initialize the MIMIC-CXR loader.
        
        Args:
            csv_path: Path to mimic-cxr.csv file
        """
        self.csv_path = Path(csv_path)
        self.df = None
        self._load_data()
    
    def _load_data(self):
        """Load the CSV file into a DataFrame."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"MIMIC-CXR CSV file not found: {self.csv_path}")
        
        try:
            self.df = pd.read_csv(self.csv_path)
            # Create a lookup dictionary for faster access
            self._create_lookup()
        except Exception as e:
            raise ValueError(f"Failed to load MIMIC-CXR CSV: {e}") from e
    
    def _create_lookup(self):
        """Create a lookup dictionary mapping filename to labels."""
        self.lookup = {}
        for _, row in self.df.iterrows():
            filename = row['filename']
            labels = self._extract_labels_from_row(row)
            self.lookup[filename] = labels
    
    def _extract_labels_from_row(self, row: pd.Series) -> List[str]:
        """
        Extract CheXpert labels from a CSV row.
        
        Args:
            row: Pandas Series representing a row from the CSV
            
        Returns:
            List of label names where value is 1.0
        """
        labels = []
        
        # CheXpert label columns (excluding filename, split, label)
        label_columns = [
            'Atelectasis', 'Cardiomegaly', 'Consolidation', 'Edema',
            'Enlarged Cardiomediastinum', 'Lung Lesion', 'Lung Opacity',
            'Normal', 'Pleural Effusion', 'Pneumonia', 'Pneumothorax'
        ]
        
        for col in label_columns:
            if col in row and row[col] == 1.0:
                labels.append(col)
        
        # If no labels found and Normal is 0, return empty list
        # If Normal is 1.0, return ["No Finding"]
        if not labels and row.get('Normal', 0) == 1.0:
            return ["No Finding"]
        
        return labels
    
    def get_labels(self, filename: str) -> Optional[List[str]]:
        """
        Get CheXpert labels for a given filename.
        
        Args:
            filename: Image filename (e.g., "s50000014.jpg")
            
        Returns:
            List of CheXpert labels, or None if not found
        """
        # Try exact match first
        if filename in self.lookup:
            return self.lookup[filename]
        
        # Try with just the base filename (without path)
        base_filename = Path(filename).name
        if base_filename in self.lookup:
            return self.lookup[base_filename]
        
        # Try case-insensitive match
        filename_lower = filename.lower()
        base_filename_lower = base_filename.lower()
        
        for key in self.lookup.keys():
            if key.lower() == filename_lower or key.lower() == base_filename_lower:
                return self.lookup[key]
        
        return None
    
    def get_labels_with_metadata(self, filename: str) -> Optional[Dict]:
        """
        Get labels with additional metadata from the dataset.
        
        Args:
            filename: Image filename
            
        Returns:
            Dictionary with labels and metadata, or None if not found
        """
        base_filename = Path(filename).name
        
        # Find matching row
        matching_row = self.df[self.df['filename'] == base_filename]
        
        if matching_row.empty:
            # Try case-insensitive
            matching_row = self.df[
                self.df['filename'].str.lower() == base_filename.lower()
            ]
        
        if matching_row.empty:
            return None
        
        row = matching_row.iloc[0]
        labels = self._extract_labels_from_row(row)
        
        return {
            "labels": labels,
            "split": row.get('split', 'unknown'),
            "label_text": row.get('label', ''),
            "filename": row.get('filename', filename)
        }
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the dataset.
        
        Returns:
            Dictionary with dataset statistics
        """
        if self.df is None:
            return {}
        
        total_images = len(self.df)
        train_count = len(self.df[self.df['split'] == 'train'])
        test_count = len(self.df[self.df['split'] == 'test'])
        val_count = len(self.df[self.df['split'] == 'val'])
        
        # Count label frequencies
        label_counts = {}
        label_columns = [
            'Atelectasis', 'Cardiomegaly', 'Consolidation', 'Edema',
            'Enlarged Cardiomediastinum', 'Lung Lesion', 'Lung Opacity',
            'Normal', 'Pleural Effusion', 'Pneumonia', 'Pneumothorax'
        ]
        
        for col in label_columns:
            if col in self.df.columns:
                label_counts[col] = int(self.df[col].sum())
        
        return {
            "total_images": total_images,
            "train": train_count,
            "test": test_count,
            "val": val_count,
            "label_frequencies": label_counts
        }
    
    def search_by_labels(self, labels: List[str]) -> List[str]:
        """
        Find filenames that have specific labels.
        
        Args:
            labels: List of label names to search for
            
        Returns:
            List of filenames matching the labels
        """
        if self.df is None:
            return []
        
        # Create a mask for rows that have all specified labels
        mask = pd.Series([True] * len(self.df))
        
        for label in labels:
            if label == "No Finding":
                mask = mask & (self.df['Normal'] == 1.0)
            elif label in self.df.columns:
                mask = mask & (self.df[label] == 1.0)
            else:
                # Label not found in dataset
                return []
        
        matching_rows = self.df[mask]
        return matching_rows['filename'].tolist()

