#!/usr/bin/env python3
"""
YAAP - Yet Another AI Program
A simple and light AI Terminal application
"""

import sys
import argparse
import asyncio
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from chat.session import ChatSession


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="YAAP - Yet Another AI Program",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  yaap                    Start interactive chat session
  yaap Hello AI           Ask a direct question
  yaap "How are you?"     Ask a question with spaces
        """
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
    
    parser.add_argument(
        "query",
        nargs="*",
        help="Direct query to ask the AI (if not provided, starts interactive mode)"
    )
    
    return parser.parse_args()


async def handle_direct_query(query: str, debug: bool = False):
    """Handle a direct query and return response"""
    session = ChatSession(debug=debug)
    response = await session.get_ai_response(query)
    print(session.formatter.format_response(response))


async def main_async():
    """Async main function"""
    args = parse_args()
    
    # Check if we have a direct query
    if args.query:
        # Join all query arguments into a single string
        query = " ".join(args.query)
        try:
            await handle_direct_query(query, args.debug)
        except Exception as e:
            if args.debug:
                raise
            print(f"Error: {e}")
            sys.exit(1)
        return
    
    # Interactive mode
    session = ChatSession(debug=args.debug)
    
    # Welcome message
    print("YAAP - Yet Another AI Program")
    print("Type 'exit' or 'quit' to end the session")
    print("Type 'help' for available commands")
    print("-" * 50)
    
    try:
        # Start interactive session
        await session.start()
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
        sys.exit(0)
    except Exception as e:
        if args.debug:
            raise
        print(f"\nError: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()