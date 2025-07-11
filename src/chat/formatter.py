"""
Message formatting and display utilities for YAAP
"""

import textwrap
import shutil
from typing import Optional


class MessageFormatter:
    """Handles formatting and display of chat messages"""
    
    def __init__(self, max_width: Optional[int] = None):
        # Get terminal width, default to 80 if not available
        self.max_width = max_width or min(shutil.get_terminal_size().columns, 100)
        self.indent = "  "
        
        # ANSI color codes
        self.LIGHT_PURPLE = '\033[38;5;183m'  # Soft light purple
        self.RESET = '\033[0m'
        
    def format_message(self, content: str, role: str = "assistant") -> str:
        """Format a message for display"""
        if role == "user":
            return self._format_user_message(content)
        else:
            return self._format_assistant_message(content)
    
    def _format_user_message(self, content: str) -> str:
        """Format user message (default/white color)"""
        wrapped = textwrap.fill(
            content,
            width=self.max_width - len(self.indent),
            initial_indent=self.indent,
            subsequent_indent=self.indent
        )
        return wrapped
    
    def _format_assistant_message(self, content: str) -> str:
        """Format assistant message (light purple, no indentation)"""
        wrapped = textwrap.fill(
            content,
            width=self.max_width,
            initial_indent="",
            subsequent_indent=""
        )
        return f"{self.LIGHT_PURPLE}{wrapped}{self.RESET}"
    
    def format_response(self, response: str) -> str:
        """Format AI response with light purple color"""
        return self._format_assistant_message(response)
    
    def format_error(self, error_msg: str) -> str:
        """Format error message"""
        wrapped = textwrap.fill(
            error_msg,
            width=self.max_width - 4,
            initial_indent="[Error!] ",
            subsequent_indent="   "
        )
        return wrapped
    
    def format_info(self, info_msg: str) -> str:
        """Format info message"""
        wrapped = textwrap.fill(
            info_msg,
            width=self.max_width - 4,
            initial_indent="[Info] ",
            subsequent_indent="   "
        )
        return wrapped
    
    def format_debug(self, debug_msg: str) -> str:
        """Format debug message"""
        wrapped = textwrap.fill(
            debug_msg,
            width=self.max_width - 4,
            initial_indent="[Debug] ",
            subsequent_indent="   "
        )
        return wrapped