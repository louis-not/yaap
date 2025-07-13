"""
Streaming utilities for YAAP
Handles real-time postprocessing of streaming responses
"""

import re
import asyncio
from typing import AsyncGenerator, Optional, Callable
from .helpers import postprocess_response


class StreamingPostprocessor:
    """
    Handles postprocessing of streaming text chunks in real-time
    Buffers text when necessary to handle thinking tokens properly
    """
    
    def __init__(self, remove_thinking: bool = True, thinking_callback: Optional[Callable] = None):
        self.remove_thinking = remove_thinking
        self.thinking_callback = thinking_callback
        self.buffer = ""
        self.in_thinking_block = False
        self.thinking_depth = 0
        self.thinking_content_length = 0
    
    def reset(self):
        """Reset the processor state"""
        self.buffer = ""
        self.in_thinking_block = False
        self.thinking_depth = 0
        self.thinking_content_length = 0
    
    def process_chunk(self, chunk: str) -> str:
        """
        Process a single chunk of streaming text
        
        Args:
            chunk: Text chunk from streaming response
            
        Returns:
            Processed chunk that should be displayed (may be empty)
        """
        if not self.remove_thinking:
            return chunk
        
        # Add chunk to buffer
        self.buffer += chunk
        output = ""
        
        # Process the buffer
        i = 0
        while i < len(self.buffer):
            # Look for thinking token patterns
            remaining = self.buffer[i:].lower()
            
            # Check for opening thinking tag
            think_start = remaining.find('<think>')
            if think_start == 0 and not self.in_thinking_block:
                # Found opening tag at current position
                self.in_thinking_block = True
                self.thinking_depth = 1
                self.thinking_content_length = 0
                # Skip callback for now - will be handled differently
                i += 7  # Skip '<think>'
                continue
            
            # Check for closing thinking tag  
            think_end = remaining.find('</think>')
            if think_end == 0 and self.in_thinking_block:
                # Found closing tag at current position
                self.thinking_depth -= 1
                if self.thinking_depth <= 0:
                    self.in_thinking_block = False
                    self.thinking_depth = 0
                    # Skip callback for now - will be handled differently
                i += 8  # Skip '</think>'
                continue
            
            # Check for nested opening tag within thinking block
            if self.in_thinking_block and think_start >= 0 and (think_end < 0 or think_start < think_end):
                # Skip to after the nested opening tag
                self.thinking_depth += 1
                i += think_start + 7
                continue
            
            # If we're not in a thinking block, add character to output
            if not self.in_thinking_block:
                # Look ahead to see if we're about to enter a thinking block
                if think_start >= 0 and think_start < 10:  # Look ahead a bit
                    # We might be about to enter a thinking block
                    # Only output up to the thinking tag
                    safe_length = think_start
                    output += self.buffer[i:i + safe_length]
                    i += safe_length
                else:
                    # Safe to output this character
                    output += self.buffer[i]
                    i += 1
            else:
                # We're in a thinking block, skip this character
                self.thinking_content_length += 1
                # Skip progress callback for now
                i += 1
        
        # Keep only unprocessed part in buffer
        # If we're in middle of processing, keep some buffer
        if self.in_thinking_block or (len(self.buffer) > 0 and self.buffer[-10:].lower().find('<think') >= 0):
            # Keep the buffer as we might be in the middle of a tag
            pass
        else:
            # Clear processed content from buffer
            processed_length = len(self.buffer) - max(0, len(self.buffer) - 20)  # Keep last 20 chars as safety
            self.buffer = self.buffer[processed_length:]
        
        return output
    
    def finalize(self) -> str:
        """
        Finalize processing and return any remaining content
        
        Returns:
            Any remaining content that should be displayed
        """
        if not self.remove_thinking:
            remaining = self.buffer
            self.buffer = ""
            return remaining
        
        # Process any remaining buffer content
        if self.buffer and not self.in_thinking_block:
            # Apply final postprocessing to remaining content
            remaining = postprocess_response(self.buffer, remove_thinking=True)
            self.buffer = ""
            return remaining
        
        # Clear buffer and return empty string
        self.buffer = ""
        return ""


async def process_streaming_response(
    stream: AsyncGenerator[str, None], 
    remove_thinking: bool = True,
    thinking_callback: Optional[Callable] = None
) -> AsyncGenerator[str, None]:
    """
    Process a streaming response with postprocessing
    
    Args:
        stream: Input stream of text chunks
        remove_thinking: Whether to remove thinking tokens
        thinking_callback: Callback for thinking state changes
        
    Yields:
        Processed text chunks
    """
    processor = StreamingPostprocessor(
        remove_thinking=remove_thinking,
        thinking_callback=thinking_callback
    )
    
    try:
        async for chunk in stream:
            if chunk:
                processed_chunk = processor.process_chunk(chunk)
                if processed_chunk:
                    yield processed_chunk
    finally:
        # Yield any remaining content
        final_chunk = processor.finalize()
        if final_chunk:
            yield final_chunk