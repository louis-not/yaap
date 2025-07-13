"""
Thinking animation utilities for YAAP
Shows animated thinking indicator when AI is processing inside thinking tokens
"""

import asyncio
import sys
from typing import Optional


class ThinkingAnimator:
    """Handles the thinking animation display"""
    
    def __init__(self, color_code: str = '\033[38;5;183m'):
        self.color_code = color_code
        self.reset_code = '\033[0m'
        self.animation_task: Optional[asyncio.Task] = None
        self.is_active = False
        self.animation_frames = [
            "thinking",
            "thinking.",
            "thinking..",
            "thinking...",
            "thinking..",
            "thinking."
        ]
        self.current_frame = 0
    
    async def start_animation(self):
        """Start the thinking animation"""
        if self.is_active:
            return
        
        self.is_active = True
        self.current_frame = 0
        
        # Clear any existing content and show first frame
        print(f"\r{self.color_code}{self.animation_frames[0]}{self.reset_code}", end='', flush=True)
        
        # Start animation loop
        self.animation_task = asyncio.create_task(self._animate())
    
    async def stop_animation(self):
        """Stop the thinking animation and clear the line"""
        if not self.is_active:
            return
        
        self.is_active = False
        
        if self.animation_task:
            self.animation_task.cancel()
            try:
                await self.animation_task
            except asyncio.CancelledError:
                pass
            self.animation_task = None
        
        # Clear the thinking line
        print(f"\r{' ' * 15}\r", end='', flush=True)
    
    async def _animate(self):
        """Animation loop"""
        try:
            while self.is_active:
                await asyncio.sleep(0.5)  # Animation speed
                if self.is_active:
                    self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
                    frame = self.animation_frames[self.current_frame]
                    print(f"\r{self.color_code}{frame}{self.reset_code}", end='', flush=True)
        except asyncio.CancelledError:
            pass
    
    def update_progress(self):
        """Called periodically during thinking to keep animation alive"""
        # Animation is handled by the async loop, no action needed
        pass


class StreamingThinkingHandler:
    """Handles thinking animation during streaming responses"""
    
    def __init__(self, color_code: str = '\033[38;5;183m'):
        self.animator = ThinkingAnimator(color_code)
        self.thinking_active = False
    
    async def handle_thinking_event(self, event: str):
        """Handle thinking state changes"""
        if event == "enter":
            if not self.thinking_active:
                self.thinking_active = True
                await self.animator.start_animation()
        elif event == "exit":
            if self.thinking_active:
                self.thinking_active = False
                await self.animator.stop_animation()
        elif event == "progress":
            if self.thinking_active:
                self.animator.update_progress()
    
    async def cleanup(self):
        """Clean up any active animations"""
        if self.thinking_active:
            self.thinking_active = False
            await self.animator.stop_animation()