import re
import gc
import torch

from mira.text_processing import normalize_text, NormalizationOptions


def split_text(text, normalize=True, normalization_options=None):
    """
    Split text into sentences with optional normalization.
    
    Args:
        text: Input text to split
        normalize: Whether to normalize text before splitting
        normalization_options: NormalizationOptions instance for customizing normalization
        
    Returns:
        List of sentence strings
    """
    if normalize:
        if normalization_options is None:
            normalization_options = NormalizationOptions()
        text = normalize_text(text, normalization_options)
    
    # Split by sentence-ending punctuation
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Filter out empty strings
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences


def clear_cache():
    gc.collect()
    torch.cuda.empty_cache()
