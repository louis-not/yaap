"""
Chat session management for YAAP
"""

import time
import asyncio
from typing import List, Dict, Optional
from .formatter import MessageFormatter
from llm import OpenAIClient, Message, MessageRole
from config import load_llm_config


class ChatSession:
    """Manages chat session state and conversation flow"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.conversation_history: List[Dict[str, str]] = []
        self.formatter = MessageFormatter()
        self.session_start_time = time.time()
        
        # Initialize LLM client
        try:
            config = load_llm_config()
            self.llm_client = OpenAIClient(config)
            self.use_llm = True
            if self.debug:
                print(f"[DEBUG] LLM initialized: {config.model} at {config.base_url}")
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] LLM initialization failed: {e}")
            self.llm_client = None
            self.use_llm = False
        
    def add_message(self, role: str, content: str, timestamp: Optional[float] = None):
        """Add a message to conversation history"""
        if timestamp is None:
            timestamp = time.time()
            
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp
        }
        
        self.conversation_history.append(message)
        
        if self.debug:
            print(f"[DEBUG] Added {role} message: {content[:50]}...")
    
    async def get_ai_response(self, user_input: str) -> str:
        """Generate AI response using LLM or fallback to dummy response"""
        if not self.use_llm or not self.llm_client:
            return self._get_dummy_response(user_input)
        
        try:
            # Convert conversation history to Message objects
            messages = self._prepare_messages_for_llm(user_input)
            
            # Generate response using LLM
            response = await self.llm_client.generate(messages)
            return response.content
            
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] LLM request failed: {e}")
            # Fallback to dummy response
            return self._get_dummy_response(user_input)
    
    def _get_dummy_response(self, user_input: str) -> str:
        """Generate a dummy AI response as fallback"""
        responses = [
            "I'm an AI assistant, I'm ready to help! You said: '{}'".format(user_input),
            "That's interesting! I'm still learning, but I appreciate you sharing that.",
            "I understand you're asking about '{}'. As a simple AI, I'm here to assist you.".format(user_input),
            "Thank you for your message. I'm an AI assistant ready to help with your questions.",
            "I see you mentioned '{}'. I'm here to help however I can!".format(user_input)
        ]
        
        # Simple response selection based on input length
        response_index = len(user_input) % len(responses)
        return responses[response_index]
    
    def _prepare_messages_for_llm(self, current_input: str) -> List[Message]:
        """Convert conversation history to LLM Message format"""
        messages = []
        
        # Add system message
        system_prompt = (
            "You are YAAP (Yet Another AI Program), a helpful AI assistant. "
            "Be concise, friendly, and helpful in your responses."
        )
        messages.append(Message(MessageRole.SYSTEM, system_prompt))
        
        # Add conversation history
        for msg in self.conversation_history:
            role = MessageRole.USER if msg["role"] == "user" else MessageRole.ASSISTANT
            messages.append(Message(role, msg["content"]))
        
        # Add current user input
        messages.append(Message(MessageRole.USER, current_input))
        
        return messages
    
    def handle_command(self, command: str) -> bool:
        """Handle special commands. Returns True if command was handled."""
        command = command.lower().strip()
        
        if command in ['exit', 'quit']:
            self.show_session_summary()
            return True
            
        elif command == 'help':
            self.show_help()
            return True
            
        elif command == 'history':
            self.show_history()
            return True
            
        elif command == 'clear':
            self.clear_history()
            return True
            
        return False
    
    def show_help(self):
        """Display help information"""
        help_text = """
Available commands:
  help     - Show this help message
  history  - Show conversation history
  clear    - Clear conversation history
  exit     - Exit the program
  quit     - Exit the program
  
Simply type your message and press Enter to chat!
        """
        print(help_text)
    
    def show_history(self):
        """Display conversation history"""
        if not self.conversation_history:
            print("No conversation history yet.")
            return
            
        print("\n" + "="*50)
        print("CONVERSATION HISTORY")
        print("="*50)
        
        for i, message in enumerate(self.conversation_history, 1):
            timestamp = time.strftime("%H:%M:%S", time.localtime(message["timestamp"]))
            role = message["role"].upper()
            content = message["content"]
            
            print(f"\n[{i}] {timestamp} - {role}:")
            print(self.formatter.format_message(content, role.lower()))
        
        print("="*50 + "\n")
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        print("Conversation history cleared.")
    
    def show_session_summary(self):
        """Show session summary before exit"""
        duration = time.time() - self.session_start_time
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        print(f"\nSession Summary:")
        print(f"Duration: {minutes}m {seconds}s")
        print(f"Messages exchanged: {len(self.conversation_history)}")
        print("Thank you for using YAAP! 🤖")
    
    async def start(self):
        """Start the interactive chat session"""
        print("Chat session started. Type your message below:\n")
        
        while True:
            try:
                # Get user input (no prefix, default color)
                user_input = input().strip()
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Handle special commands
                if self.handle_command(user_input):
                    break
                
                # Add user message to history
                self.add_message("user", user_input)
                
                # Get AI response using LLM
                ai_response = await self.get_ai_response(user_input)
                
                # Add AI response to history
                self.add_message("assistant", ai_response)
                
                # Display formatted AI response
                print(self.formatter.format_response(ai_response))
                print()  # Empty line for readability
                
            except EOFError:
                # Handle Ctrl+D
                print("\nGoodbye! 👋")
                break
            except KeyboardInterrupt:
                # Handle Ctrl+C
                raise