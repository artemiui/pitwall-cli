"""Interactive CLI entrypoint."""

import sys

from .colors import Color
from .commands import process_command
from .state import ctx


def interactive_mode():
    """Run in interactive mode."""
    print(f"{Color.GREEN}{Color.BOLD}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║                      PITWALL-CLI                       ║")
    print("║                  F1 Data from OpenF1                   ║")
    print("║                      by @artemiui                      ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"{Color.RESET}")
    print(f"{Color.CYAN}Type a year (e.g., '2024') to start browsing{Color.RESET}")
    print(f"{Color.CYAN}Type 'help' for all commands or 'exit' to quit{Color.RESET}\n")

    while True:
        try:
            if ctx.current_driver:
                prompt = f"{Color.MAGENTA}f1/driver-{ctx.current_driver}>{Color.RESET} "
            elif ctx.current_session_key:
                prompt = f"{Color.BLUE}f1/session-{ctx.current_session_key}>{Color.RESET} "
            elif ctx.current_year:
                prompt = f"{Color.YELLOW}f1/{ctx.current_year}>{Color.RESET} "
            else:
                prompt = f"{Color.GREEN}f1>{Color.RESET} "

            user_input = input(prompt).strip()
            if not user_input:
                continue

            args = user_input.split()
            if not process_command(args):
                print(f"\n{Color.YELLOW}Goodbye! 🏁{Color.RESET}")
                break

        except KeyboardInterrupt:
            print(f"\n{Color.YELLOW}Use 'exit' to quit or 'back' to go back{Color.RESET}")
        except EOFError:
            print(f"\n{Color.YELLOW}Goodbye! 🏁{Color.RESET}")
            break


def main():
    """Main CLI handler."""
    if len(sys.argv) < 2:
        interactive_mode()
    else:
        process_command(sys.argv[1:])


if __name__ == "__main__":
    main()


