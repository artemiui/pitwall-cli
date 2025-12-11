"""Shared display helpers."""

from .colors import Color


def print_header(text: str):
    """Print a styled header."""
    print(f"\n{Color.GREEN}{Color.BOLD}{'='*60}{Color.RESET}")
    print(f"{Color.RED}{Color.BOLD}{text.center(60)}{Color.RESET}")
    print(f"{Color.GREEN}{Color.BOLD}{'='*60}{Color.RESET}\n")


def print_section(text: str):
    """Print a section header."""
    print(f"{Color.CYAN}{Color.BOLD}▶ {text}{Color.RESET}")
    print(f"{Color.DIM}{'─'*60}{Color.RESET}")


