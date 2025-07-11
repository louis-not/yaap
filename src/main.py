#!/usr/bin/env python3
"""
YAAP - Yet Another AI Program
A simple and light AI Terminal application
"""

import sys
import argparse
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from chat.session import ChatSession


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="YAAP - Yet Another AI Program",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="YAAP 0.1.0"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()
    
    # Initialize chat session
    session = ChatSession(debug=args.debug)
    
    # Welcome message
    print("> YAAP - Yet Another AI Program")
    print("Type 'exit' or 'quit' to end the session")
    print("Type 'help' for available commands")
    print("-" * 50)
    
    try:
        # Start interactive session
        session.start()
    except KeyboardInterrupt:
        print("\n\nGoodbye! =K")
        sys.exit(0)
    except Exception as e:
        if args.debug:
            raise
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()