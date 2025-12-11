"""Command parsing and routing."""

import os
from datetime import datetime
from typing import List

from .colors import Color
from .display import print_header
from .state import ctx, f1_cache
from .views import (
    export_data,
    show_current_gp,
    show_driver_all,
    show_driver_laps,
    show_driver_menu,
    show_driver_pits,
    show_driver_position,
    show_driver_radio,
    show_driver_stints,
    show_meeting_sessions,
    show_session_drivers,
    show_year_meetings,
)


def show_help():
    """Show help menu."""
    print_header("F1 CLI - HELP")

    commands = [
        ("gp, current", "Show current and next Grand Prix"),
        ("[year]", "Show all Grand Prix for a year (e.g., 2024)"),
        ("[meeting_key]", "Show sessions for a Grand Prix"),
        ("[session_key]", "Show drivers in a session"),
        ("[driver_number]", "Show data menu for driver"),
        ("laps/stints/pit/radio", "Show specific driver data"),
        ("export <endpoint> <params>", "Export data (auto-adds context)"),
        ("context, where", "Show current navigation position"),
        ("clear", "Clear screen and refresh current view"),
        ("back", "Go back to previous screen"),
        ("help", "Show this help menu"),
        ("exit, quit, q", "Exit interactive mode"),
        ("export <endpoint> [params]", "Export data (JSON default, CSV with format=csv)"),
    ]

    print(f"{Color.YELLOW}{Color.BOLD}NAVIGATION FLOW:{Color.RESET}")
    print(f"  {Color.CYAN}Year → Grand Prix → Session → Driver → Data{Color.RESET}\n")

    print(f"{Color.YELLOW}{Color.BOLD}COMMANDS:{Color.RESET}")
    for cmd, desc in commands:
        print(f"  {Color.GREEN}{cmd:<35}{Color.RESET} {desc}")

    print(f"\n{Color.YELLOW}{Color.BOLD}EXAMPLES:{Color.RESET}")
    print(f"  {Color.CYAN}2024{Color.RESET}          # Show all 2024 Grand Prix")
    print(f"  {Color.CYAN}1056{Color.RESET}          # Select Grand Prix 1056")
    print(f"  {Color.CYAN}9636{Color.RESET}          # Select session 9636")
    print(f"  {Color.CYAN}44{Color.RESET}            # Select driver #44")
    print(f"  {Color.CYAN}laps{Color.RESET}          # View lap times")
    print(f"  {Color.CYAN}export laps{Color.RESET}   # Export lap data (uses context)")
    print(f"  {Color.CYAN}back{Color.RESET}          # Go back one level")
    print(f"  {Color.CYAN}context{Color.RESET}       # Show where you are")
    print(f"\n{Color.YELLOW}{Color.BOLD}EXPORT EXAMPLES:{Color.RESET}")
    print(f"  {Color.CYAN}export laps format=csv{Color.RESET}")
    print(f"  {Color.CYAN}export laps format=csv session_key=9636{Color.RESET}")
    print(f"  {Color.CYAN}export stints format=csv session_key=9636 driver_number=44{Color.RESET}")
    print(f"  {Color.CYAN}export meetings format=csv year=2024{Color.RESET}")
    print(f"  {Color.CYAN}export sessions format=csv meeting_key=1056{Color.RESET}")


def process_command(args: List[str]) -> bool:
    """Process a single command. Returns False if should exit."""
    if not args:
        return True

    command = args[0].lower()

    if command in ["exit", "quit", "q"]:
        return False

    if command == "back":
        if ctx.current_driver:
            ctx.current_driver = None
            show_session_drivers(ctx.current_session_key)
        elif ctx.current_session_key:
            ctx.current_session_key = None
            show_meeting_sessions(ctx.current_meeting_key)
        elif ctx.current_meeting_key:
            ctx.current_meeting_key = None
            if ctx.current_year:
                show_year_meetings(ctx.current_year)
            else:
                print(f"{Color.YELLOW}Returned to main menu{Color.RESET}")
        elif ctx.current_year:
            ctx.current_year = None
            print(f"{Color.YELLOW}Returned to main menu{Color.RESET}")
        else:
            print(f"{Color.YELLOW}Already at main menu{Color.RESET}")
        return True

    try:
        if ctx.current_driver and ctx.current_session_key:
            if command == "laps":
                show_driver_laps(ctx.current_session_key, ctx.current_driver)
            elif command == "stints":
                show_driver_stints(ctx.current_session_key, ctx.current_driver)
            elif command == "position":
                show_driver_position(ctx.current_session_key, ctx.current_driver)
            elif command == "pit":
                show_driver_pits(ctx.current_session_key, ctx.current_driver)
            elif command == "radio":
                show_driver_radio(ctx.current_session_key, ctx.current_driver)
            elif command == "car":
                print(
                    f"{Color.YELLOW}Car telemetry requires specific time ranges. Use export command.{Color.RESET}"
                )
            elif command == "all":
                show_driver_all(ctx.current_session_key, ctx.current_driver)
            else:
                print(f"{Color.RED}Unknown driver data command: {command}{Color.RESET}")
                print("Available: laps, stints, position, pit, radio, all")
            return True

        if command.isdigit() and ctx.current_session_key and not ctx.current_driver:
            show_driver_menu(ctx.current_session_key, command)
            return True

        if command.isdigit() and ctx.current_meeting_key and not ctx.current_session_key:
            session_exists = False
            for session in ctx.sessions_cache:
                if str(session["session_key"]) == command:
                    session_exists = True
                    break

            if session_exists:
                show_session_drivers(command)
            else:
                print(f"{Color.RED}Session key {command} not found in current meeting{Color.RESET}")
                print("Type 'back' to return to session list")
            return True

        if command.isdigit() and ctx.current_year and not ctx.current_meeting_key:
            meeting_exists = False
            for meeting in ctx.meetings_cache:
                if str(meeting["meeting_key"]) == command:
                    meeting_exists = True
                    break

            if meeting_exists:
                show_meeting_sessions(command)
            else:
                print(f"{Color.RED}Meeting key {command} not found in {ctx.current_year}{Color.RESET}")
                print("Type 'back' to return to meetings list")
            return True

        if command.isdigit() and len(command) == 4:
            year = int(command)
            if 1950 <= year <= datetime.now().year + 1:
                show_year_meetings(year)
            else:
                print(
                    f"{Color.RED}Please enter a valid F1 year (1950-{datetime.now().year + 1}){Color.RESET}"
                )
            return True

        if command in ["gp", "current"]:
            show_current_gp()
            return True

        if command == "export":
            if len(args) < 2:
                print(
                    f"{Color.RED}Usage: export <endpoint> [format=json|csv] [key=value ...]{Color.RESET}"
                )
                print("Examples:")
                print(f"  {Color.CYAN}export laps format=csv{Color.RESET}")
                print(f"  {Color.CYAN}export laps format=csv session_key=1234 driver_number=44{Color.RESET}")
                print(f"  {Color.CYAN}export meetings format=csv year=2024{Color.RESET}")
                return True

            endpoint = args[1]
            params = {}
            export_format = "json"

            for arg in args[2:]:
                if "=" in arg:
                    k, v = arg.split("=", 1)
                    if k == "format":
                        if v.lower() in ["json", "csv"]:
                            export_format = v.lower()
                        else:
                            print(
                                f"{Color.YELLOW}Warning: Format '{v}' not supported. Using JSON.{Color.RESET}"
                            )
                    else:
                        params[k] = v
                else:
                    print(f"{Color.YELLOW}Warning: Ignoring parameter '{arg}' without '='{Color.RESET}")

            if "session_key" not in params and ctx.current_session_key:
                params["session_key"] = ctx.current_session_key
                print(f"{Color.CYAN}✓ Using current session key: {ctx.current_session_key}{Color.RESET}")

            if "driver_number" not in params and ctx.current_driver:
                params["driver_number"] = ctx.current_driver
                print(f"{Color.CYAN}✓ Using current driver number: {ctx.current_driver}{Color.RESET}")

            if "year" not in params and ctx.current_year:
                params["year"] = ctx.current_year
                print(f"{Color.CYAN}✓ Using current year: {ctx.current_year}{Color.RESET}")

            if endpoint == "current":
                endpoint = "sessions"
                params["year"] = datetime.now().year
                print(f"{Color.CYAN}✓ Exporting current year sessions{Color.RESET}")

            export_data(endpoint, params, format=export_format)
            return True

        if command == "help":
            show_help()
            return True
        if command == "cache":
            if len(args) > 1:
                subcmd = args[1].lower()
                if subcmd == "clear":
                    endpoint = args[2] if len(args) > 2 else None
                    f1_cache.clear(endpoint)
                elif subcmd == "stats":
                    stats = f1_cache.stats()
                    print_header("CACHE STATISTICS")
                    print(stats)
                elif subcmd == "info":
                    print_header("CACHE INFORMATION")
                    print(f"Cache directory: {f1_cache.cache_dir}")
                else:
                    print(f"{Color.RED}Unknown cache subcommand: {subcmd}{Color.RESET}")
            else:
                print(f"{Color.RED}Usage: cache <stats|clear|info>{Color.RESET}")
            return True

        if command == "refresh":
            print(f"{Color.YELLOW}⚠ Refreshing data (bypassing cache)...{Color.RESET}")
            if ctx.current_driver:
                show_driver_menu(ctx.current_session_key, ctx.current_driver, force_refresh=True)
            elif ctx.current_session_key:
                show_session_drivers(ctx.current_session_key, force_refresh=True)
            elif ctx.current_meeting_key:
                show_meeting_sessions(ctx.current_meeting_key, force_refresh=True)
            elif ctx.current_year:
                show_year_meetings(ctx.current_year, force_refresh=True)
            else:
                print(f"{Color.YELLOW}Nothing to refresh.{Color.RESET}")
            return True

        if command == "clear":
            os.system("cls" if os.name == "nt" else "clear")
            print(f"{Color.GREEN}Screen cleared{Color.RESET}")

            if ctx.current_driver:
                show_driver_menu(ctx.current_session_key, ctx.current_driver)
            elif ctx.current_session_key:
                show_session_drivers(ctx.current_session_key)
            elif ctx.current_meeting_key:
                show_meeting_sessions(ctx.current_meeting_key)
            elif ctx.current_year:
                show_year_meetings(ctx.current_year)
            return True

        if command in ["context", "where"]:
            print_header("CURRENT CONTEXT")
            if ctx.current_year:
                print(f"{Color.CYAN}Year: {ctx.current_year}{Color.RESET}")
            if ctx.current_meeting_key:
                meeting_name = "Unknown"
                for meeting in ctx.meetings_cache:
                    if str(meeting["meeting_key"]) == ctx.current_meeting_key:
                        meeting_name = meeting.get("meeting_name", "Unknown")
                        break
                print(
                    f"{Color.CYAN}Meeting: {meeting_name} (key: {ctx.current_meeting_key}){Color.RESET}"
                )
            if ctx.current_session_key:
                session_name = "Unknown"
                for session in ctx.sessions_cache:
                    if str(session["session_key"]) == ctx.current_session_key:
                        session_name = session.get("session_name", "Unknown")
                        break
                print(
                    f"{Color.CYAN}Session: {session_name} (key: {ctx.current_session_key}){Color.RESET}"
                )
            if ctx.current_driver:
                print(f"{Color.CYAN}Driver: #{ctx.current_driver}{Color.RESET}")

            if not any(
                [
                    ctx.current_year,
                    ctx.current_meeting_key,
                    ctx.current_session_key,
                    ctx.current_driver,
                ]
            ):
                print(f"{Color.DIM}At main menu{Color.RESET}")

            print(
                f"\n{Color.YELLOW}Navigation: Year → Meeting → Session → Driver → Data{Color.RESET}"
            )
            return True

        print(f"{Color.RED}Unknown command: {command}{Color.RESET}")
        print(f"Type '{Color.GREEN}help{Color.RESET}' for usage or '{Color.CYAN}back{Color.RESET}' to navigate back")

        if ctx.current_session_key and not ctx.current_driver:
            print(f"Type a {Color.YELLOW}driver number{Color.RESET} to select a driver")
        elif ctx.current_meeting_key and not ctx.current_session_key:
            print(f"Type a {Color.YELLOW}session key{Color.RESET} to select a session")
        elif ctx.current_year and not ctx.current_meeting_key:
            print(f"Type a {Color.YELLOW}meeting key{Color.RESET} to select a Grand Prix")
        elif not ctx.current_year:
            print(f"Type a {Color.YELLOW}year{Color.RESET} (e.g., 2024) to start browsing")

    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Interrupted{Color.RESET}")
    except Exception as e:  # pragma: no cover - runtime safeguard
        print(f"{Color.RED}Error processing command: {e}{Color.RESET}")
        import traceback

        traceback.print_exc()

    return True


