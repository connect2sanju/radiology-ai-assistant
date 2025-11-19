from typing import List, Dict

def compare_labels_with_report(
    labels: List[str], 
    report_text: str, 
    radlex_dict: Dict[str, List[str]]
) -> tuple[List[str], List[str]]:
    """
    Compare CheXpert labels with the generated radiology report.
    
    Args:
        labels: List of CheXpert labels to check
        report_text: The generated radiology report text
        radlex_dict: Dictionary mapping labels to lists of RadLex keywords
        
    Returns:
        Tuple of (matched_labels, missed_labels)
    """
    matched = []
    missed = []

    for label in labels:
        keywords = radlex_dict.get(label, [])
        if any(term.lower() in report_text.lower() for term in keywords):
            matched.append(label)
        else:
            missed.append(label)

    return matched, missed
