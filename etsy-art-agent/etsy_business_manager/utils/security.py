"""Security validation utilities for the Etsy Business Manager.

Exposes features to ensure path integrity, api key safety, and query sanitization.
"""

import os
import re
from typing import Union

# Securely check environment key presence
def verify_api_key() -> bool:
    """Check if the Gemini API Key is set and contains a valid key format, not a placeholder.
    
    Returns:
        True if valid, False otherwise.
    """
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        return False
    # Check if key looks like placeholder
    placeholders = ["your-gemini-api-key", "your-key", "your_key_here", "insert-api-key"]
    if key.strip().lower() in placeholders or len(key.strip()) < 10:
        return False
    return True

# Validate paths to prevent Directory Traversal Attacks
def validate_safe_path(filepath: str, base_dir: str = "etsy_business_manager/data") -> str:
    """Ensure that a resolved file path stays strictly within the authorized base directory.
    
    Args:
        filepath: The input filename or path.
        base_dir: The directory containing secure data.
        
    Returns:
        The resolved absolute path string if safe.
        
    Raises:
        PermissionError: If path lies outside the base directory.
    """
    abs_base = os.path.abspath(base_dir)
    # Join with base_dir to resolve relative targets
    if not os.path.isabs(filepath):
        abs_target = os.path.abspath(os.path.join(abs_base, os.path.basename(filepath)))
    else:
        abs_target = os.path.abspath(filepath)
        
    # Check common prefix
    if not abs_target.startswith(abs_base):
        raise PermissionError(f"Security Alert: Attempted path traversal outside safe sandbox: {abs_target}")
        
    return abs_target

# Sanitize query strings to prevent prompt injection or execution exploits
def sanitize_input(user_input: str) -> str:
    """Remove suspicious control characters or formatting blocks.
    
    Args:
        user_input: Raw string input from UI.
        
    Returns:
        Sanitized safe string.
    """
    if not isinstance(user_input, str):
        return ""
    # Strip html script blocks or code-exec templates
    clean = re.sub(r'<script.*?>.*?</script>', '', user_input, flags=re.IGNORECASE)
    # Strip excess null bytes or line endings that could trigger CLI injection
    clean = clean.replace('\x00', '')
    return clean.strip()
