"""
Helper utilities for YAAP
"""

import re
from typing import Optional


def remove_thinking_tokens(text: str) -> str:
    """
    Remove thinking tokens (<think>...</think>) from text
    
    Args:
        text: Input text that may contain thinking tokens
        
    Returns:
        Text with thinking tokens removed and cleaned up
    """
    if not text:
        return text
    
    # Pattern to match <think>...</think> blocks (case insensitive, multiline)
    # This handles nested tags by using a non-greedy match
    pattern = r'<think>.*?</think>'
    
    # Remove all thinking token blocks
    cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Clean up multiple consecutive newlines (more than 2)
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    # Clean up leading/trailing whitespace
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text


def remove_thinking_tokens_advanced(text: str) -> str:
    """
    Advanced thinking token removal that handles nested and malformed tags
    
    Args:
        text: Input text that may contain thinking tokens
        
    Returns:
        Text with thinking tokens removed
    """
    if not text:
        return text
    
    result = []
    i = 0
    length = len(text)
    
    while i < length:
        # Look for opening <think> tag (case insensitive)
        think_start = text.lower().find('<think>', i)
        
        if think_start == -1:
            # No more thinking tokens, add rest of text
            result.append(text[i:])
            break
        
        # Add text before the thinking token
        result.append(text[i:think_start])
        
        # Find matching closing </think> tag
        search_pos = think_start + 7  # Length of '<think>'
        nest_level = 1
        
        while search_pos < length and nest_level > 0:
            # Look for next opening or closing tag
            next_open = text.lower().find('<think>', search_pos)
            next_close = text.lower().find('</think>', search_pos)
            
            if next_close == -1:
                # No closing tag found, skip to end
                i = length
                break
            
            if next_open != -1 and next_open < next_close:
                # Found nested opening tag
                nest_level += 1
                search_pos = next_open + 7
            else:
                # Found closing tag
                nest_level -= 1
                if nest_level == 0:
                    # Found matching closing tag
                    i = next_close + 8  # Length of '</think>'
                else:
                    search_pos = next_close + 8
    
    # Join result and clean up
    cleaned_text = ''.join(result)
    
    # Clean up multiple consecutive newlines
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    # Clean up leading/trailing whitespace
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text


def postprocess_response(text: str, remove_thinking: bool = True) -> str:
    """
    Post-process LLM response text
    
    Args:
        text: Raw response text from LLM
        remove_thinking: Whether to remove thinking tokens
        
    Returns:
        Processed response text
    """
    if not text:
        return text
    
    processed_text = text
    
    # Remove thinking tokens if requested
    if remove_thinking:
        processed_text = remove_thinking_tokens(processed_text)
    
    # Additional post-processing can be added here:
    # - Remove other unwanted tokens
    # - Format specific patterns
    # - Apply content filters
    
    return processed_text


def extract_thinking_content(text: str) -> Optional[str]:
    """
    Extract the content from thinking tokens for debugging purposes
    
    Args:
        text: Input text that may contain thinking tokens
        
    Returns:
        Extracted thinking content or None if no thinking tokens found
    """
    if not text:
        return None
    
    # Pattern to match content inside <think>...</think> blocks
    pattern = r'<think>(.*?)</think>'
    matches = re.findall(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    
    if matches:
        # Join all thinking content with separators
        return '\n--- THINKING BREAK ---\n'.join(match.strip() for match in matches)
    
    return None