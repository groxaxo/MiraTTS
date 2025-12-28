"""Schema definitions for text processing options."""

from dataclasses import dataclass


@dataclass
class NormalizationOptions:
    """Options for the text normalization system."""
    
    normalize: bool = True
    """Normalizes input text to make it easier for the model to say."""
    
    unit_normalization: bool = False
    """Transforms units like 10KB to 10 kilobytes."""
    
    url_normalization: bool = True
    """Changes urls so they can be properly pronounced."""
    
    email_normalization: bool = True
    """Changes emails so they can be properly pronounced."""
    
    optional_pluralization_normalization: bool = True
    """Replaces (s) with s so some words get pronounced correctly."""
    
    phone_normalization: bool = True
    """Changes phone numbers so they can be properly pronounced."""
    
    replace_remaining_symbols: bool = True
    """Replaces the remaining symbols after normalization with their words."""
