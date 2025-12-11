"""Presentation and data display helpers for the CLI."""

import csv
import json
from datetime import datetime
from typing import Dict, List

from .api import fetch_json
from .colors import Color
from .display import print_header, print_section
from .state import ctx


def show_year_meetings(year: int, force_refresh: bool = False):
    """Show all Grand Prix meetings for a year, grouped by location."""
    print_header(f"F1 {year} SEASON - GRAND PRIX EVENTS")

    meetings = fetch_json(
        f"https://api.openf1.org/v1/meetings?year={year}", force_refresh=force_refresh
    )

    if not meetings:
        print(f"{Color.RED}No events found for {year}{Color.RESET}")
        return

    meetings.sort(key=lambda m: m.get("date_start", ""))

    ctx.meetings_cache = meetings
    ctx.current_year = year

    print(
        f"{Color.YELLOW}{Color.BOLD}{'KEY':<8}{'ROUND':<8}{'GRAND PRIX':<25}{'LOCATION':<20}{'DATE':<12}{Color.RESET}"
    )
    print(f"{Color.DIM}{'─'*73}{Color.RESET}")

    for round_num, meeting in enumerate(meetings, start=1):
        key = meeting["meeting_key"]
        gp_name = meeting.get("meeting_name", "N/A")
        location = meeting.get("location", "N/A")
        date_str = meeting.get("date_start", "")[:10]

        if round_num == 1:
            round_color = Color.YELLOW + Color.BOLD
        elif round_num == len(meetings):
            round_color = Color.CYAN
        else:
            round_color = Color.WHITE

        print(
            f"{Color.CYAN}{key:<8}{Color.RESET}"
            f"{round_color}{round_num:<8}{Color.RESET}"
            f"{Color.GREEN}{gp_name[:24]:<25}{Color.RESET}"
            f"{Color.DIM}{location[:19]:<20}{Color.RESET}"
            f"{Color.YELLOW}{date_str:<12}{Color.RESET}"
        )

    print(
        f"\n{Color.CYAN}💡 Tip: Type a meeting key to see all sessions for that Grand Prix{Color.RESET}"
    )


def show_meeting_sessions(meeting_key: str, force_refresh: bool = False):
    """Show all practice, qualifying, and race sessions for a specific Grand Prix meeting."""
    selected_meeting = None
    for meeting in ctx.meetings_cache:
        if str(meeting["meeting_key"]) == meeting_key:
            selected_meeting = meeting
            break

    if not selected_meeting:
        print(f"{Color.RED}Meeting not found.{Color.RESET}")
        return

    print_header(f"{selected_meeting.get('meeting_name', 'Grand Prix')} - SESSIONS")

    sessions = fetch_json(
        f"https://api.openf1.org/v1/sessions?meeting_key={meeting_key}",
        force_refresh=force_refresh,
    )

    if not sessions:
        print(f"{Color.RED}No sessions found for this event.{Color.RESET}")
        return

    ctx.sessions_cache = sessions
    ctx.current_session_key = None
    ctx.current_meeting_key = meeting_key

    print(
        f"{Color.YELLOW}{Color.BOLD}{'KEY':<8}{'TYPE':<15}{'SESSION':<25}{'DATE':<12}{'TIME':<10}{Color.RESET}"
    )
    print(f"{Color.DIM}{'─'*70}{Color.RESET}")

    for session in sessions:
        key = session["session_key"]
        sess_type = session["session_type"].upper()
        sess_name = session["session_name"]

        date_start = session.get("date_start")
        if date_start:
            dt = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H:%M")
        else:
            date_str = time_str = "N/A"

        if "RACE" in sess_type:
            type_color = Color.RED
        elif "QUALIFYING" in sess_type:
            type_color = Color.YELLOW
        else:
            type_color = Color.CYAN

        print(
            f"{Color.GREEN}{key:<8}{Color.RESET}"
            f"{type_color}{sess_type:<15}{Color.RESET}"
            f"{Color.WHITE}{sess_name[:24]:<25}{Color.RESET}"
            f"{Color.DIM}{date_str:<12}{time_str:<10}{Color.RESET}"
        )

    print(f"\n{Color.CYAN}💡 Tip: Type a session key to see driver rankings{Color.RESET}")


def show_session_drivers(session_key: str, force_refresh: bool = False):
    """Show drivers for a session with rankings and let user select."""
    print_header(f"SESSION {session_key} - DRIVER RANKINGS")

    sessions = fetch_json(
        f"https://api.openf1.org/v1/sessions?session_key={session_key}",
        force_refresh=force_refresh,
    )

    if sessions:
        session = sessions[0]
        print(
            f"{Color.CYAN}{Color.BOLD}{session['session_name']} - {session['location']}{Color.RESET}"
        )
        print(f"{Color.DIM}{session['country_name']} • {session['date_start'][:10]}{Color.RESET}\n")

    results = fetch_json(
        f"https://api.openf1.org/v1/session_result?session_key={session_key}",
        force_refresh=force_refresh,
    )

    drivers = fetch_json(
        f"https://api.openf1.org/v1/drivers?session_key={session_key}",
        force_refresh=force_refresh,
    )

    if not drivers:
        print(f"{Color.RED}No driver data found{Color.RESET}")
        return

    driver_map = {
        d["driver_number"]: d for d in drivers if d.get("driver_number") is not None
    }

    ctx.current_session_key = session_key

    print(
        f"{Color.YELLOW}{Color.BOLD}{'NUM':<5}{'DRIVER':<30}{'TEAM':<30}{'POS':<5}{Color.RESET}"
    )
    print(f"{Color.DIM}{'─'*70}{Color.RESET}")

    if results:
        valid_results = [
            r
            for r in results
            if r.get("position") is not None and r.get("driver_number") is not None
        ]
        for result in sorted(valid_results, key=lambda x: x["position"]):
            pos = result["position"]
            driver_num = result["driver_number"]
            driver = driver_map.get(driver_num, {})
            name = driver.get("full_name", f"Driver {driver_num}")
            team = driver.get("team_name", "Unknown")

            if pos == 1:
                pos_color = Color.YELLOW + Color.BOLD
            elif pos <= 3:
                pos_color = Color.CYAN
            elif pos <= 10:
                pos_color = Color.GREEN
            else:
                pos_color = Color.WHITE

            print(
                f"{Color.WHITE}{driver_num:<5}{Color.RESET}"
                f"{name:<30}"
                f"{Color.DIM}{team[:29]:<30}{Color.RESET}"
                f"{pos_color}{pos:<5}{Color.RESET}"
            )
    else:
        valid_drivers = sorted(
            driver_map.values(), key=lambda x: x["driver_number"]
        )
        for driver in valid_drivers:
            num = driver["driver_number"]
            name = driver.get("full_name", "Unknown")
            team = driver.get("team_name", "Unknown")

            print(
                f"{Color.WHITE}{num:<5}{Color.RESET}"
                f"{name:<30}"
                f"{Color.DIM}{team[:29]:<30}{Color.RESET}"
                f"{Color.DIM}{'N/A':<5}{Color.RESET}"
            )

    print(f"\n{Color.CYAN}💡 Tip: Type a driver number to see their data{Color.RESET}")


def show_driver_menu(session_key: str, driver_number: str, force_refresh: bool = False):
    """Show data menu for a specific driver."""
    print_header(f"DRIVER #{driver_number} - DATA OPTIONS")

    drivers = fetch_json(
        f"https://api.openf1.org/v1/drivers?session_key={session_key}&driver_number={driver_number}",
        force_refresh=force_refresh,
    )

    if drivers:
        driver = drivers[0]
        print(f"{Color.CYAN}{Color.BOLD}{driver['full_name']}{Color.RESET}")
        print(f"{Color.DIM}{driver['team_name']} • {driver['country_code']}{Color.RESET}\n")

    ctx.current_driver = driver_number

    options = [
        ("laps", "Lap times and sector performance"),
        ("stints", "Tyre stints and strategy"),
        ("position", "Position changes during session"),
        ("pit", "Pit stop data"),
        ("car", "Car telemetry data"),
        ("radio", "Team radio messages"),
        ("all", "Show all available data"),
    ]

    print(
        f"{Color.YELLOW}{Color.BOLD}{'COMMAND':<15}{'DESCRIPTION':<45}{Color.RESET}"
    )
    print(f"{Color.DIM}{'─'*60}{Color.RESET}")

    for cmd, desc in options:
        print(f"{Color.GREEN}{cmd:<15}{Color.RESET}{desc}")

    print(
        f"\n{Color.CYAN}💡 Tip: Type a command to view driver data (e.g., 'laps')${Color.RESET}"
    )
    print(f"{Color.DIM}Or type 'back' to return to driver list{Color.RESET}")


def show_driver_laps(session_key: str, driver_number: str, force_refresh: bool = False):
    """Show lap data for a driver."""
    print_header(f"DRIVER #{driver_number} - LAP TIMES")

    laps = fetch_json(
        f"https://api.openf1.org/v1/laps?session_key={session_key}&driver_number={driver_number}",
        force_refresh=force_refresh,
    )

    if not laps:
        print(f"{Color.RED}No lap data found{Color.RESET}")
        return

    print(
        f"{Color.YELLOW}{Color.BOLD}{'LAP':<5}{'TIME':>12}{'S1':>10}{'S2':>10}{'S3':>10}{'SPEED':>8}{Color.RESET}"
    )
    print(f"{Color.DIM}{'─'*55}{Color.RESET}")

    valid_laps = [lap for lap in laps if lap.get("lap_number") is not None]
    for lap in sorted(valid_laps, key=lambda x: x["lap_number"]):
        lap_num = lap["lap_number"]
        lap_time = lap.get("lap_duration")
        s1 = lap.get("duration_sector_1")
        s2 = lap.get("duration_sector_2")
        s3 = lap.get("duration_sector_3")
        speed = lap.get("st_speed")

        time_str = f"{lap_time:.3f}s" if lap_time else "N/A"
        s1_str = f"{s1:.3f}s" if s1 else "N/A"
        s2_str = f"{s2:.3f}s" if s2 else "N/A"
        s3_str = f"{s3:.3f}s" if s3 else "N/A"
        speed_str = f"{speed} km/h" if speed else "N/A"

        print(
            f"{Color.WHITE}{lap_num:<5}{Color.RESET}"
            f"{Color.GREEN}{time_str:>12}{Color.RESET}"
            f"{Color.CYAN}{s1_str:>10}{s2_str:>10}{s3_str:>10}{Color.RESET}"
            f"{Color.YELLOW}{speed_str:>8}{Color.RESET}"
        )


def get_calculated_tyre_age(session_key: str, driver_number: str, stint_lap_start: int):
    """Calculate tyre age by fetching lap data."""
    laps = fetch_json(
        f"https://api.openf1.org/v1/laps?session_key={session_key}&driver_number={driver_number}"
    )

    if not laps:
        return 0

    for lap in laps:
        lap_num = lap.get("lap_number", 0)
        if lap_num >= stint_lap_start:
            tyre_age = lap.get("tyre_age", 0)
            if tyre_age:
                return tyre_age

    return 0


def show_driver_stints(session_key: str, driver_number: str, force_refresh: bool = False):
    """Show stint data with both accumulated age and stint progression."""
    print_header(f"DRIVER #{driver_number} - TYRE STINTS")

    stints = fetch_json(
        f"https://api.openf1.org/v1/stints?session_key={session_key}&driver_number={driver_number}",
        force_refresh=force_refresh,
    )

    if not stints:
        print(f"{Color.RED}No stint data found{Color.RESET}")
        return

    valid_stints = [s for s in stints if s.get("lap_start") is not None]
    valid_stints.sort(key=lambda x: x.get("lap_start", 0))

    print(
        f"{Color.YELLOW}{Color.BOLD}{'STINT':<6}{'TYRE':<10}{'START':<7}{'END':<7}{'ACCUM.':<8}{'PROG.':<8}{'TOTAL':<7}{Color.RESET}"
    )
    print(f"{Color.DIM}{'─'*53}{Color.RESET}")

    accumulated_age = 0

    for i, stint in enumerate(valid_stints, start=1):
        stint_num = stint.get("stint_number", i)
        compound = stint.get("compound", "N/A")
        lap_start = stint.get("lap_start", "N/A")
        lap_end = stint.get("lap_end", "N/A")

        if isinstance(lap_start, (int, float)) and isinstance(lap_end, (int, float)):
            laps_in_stint = lap_end - lap_start + 1
            progression = laps_in_stint
            total_laps = laps_in_stint

            if laps_in_stint <= 10:
                prog_color = Color.RED
            elif laps_in_stint <= 20:
                prog_color = Color.YELLOW
            else:
                prog_color = Color.GREEN
        else:
            laps_in_stint = progression = total_laps = "?"
            prog_color = Color.DIM

        api_age = (
            stint.get("tyre_age_at_start") or stint.get("tyre_age") or 0
        )

        if api_age == 0 and i > 1:
            accumulated_age += valid_stints[i - 2].get("laps_in_stint", 0) if i > 1 else 0
            display_age = accumulated_age
        else:
            display_age = api_age
            accumulated_age = api_age

        if display_age == 0:
            age_color = Color.GREEN
            age_display = "0 (new)"
        elif display_age < 10:
            age_color = Color.GREEN
            age_display = str(display_age)
        elif display_age < 20:
            age_color = Color.YELLOW
            age_display = str(display_age)
        else:
            age_color = Color.RED
            age_display = f"{display_age}+"

        compound_upper = str(compound).upper()
        if "SOFT" in compound_upper:
            compound_color = Color.RED
            compound_abbr = "S" if "SOFT" in compound_upper else compound[:3]
        elif "MEDIUM" in compound_upper:
            compound_color = Color.YELLOW
            compound_abbr = "M"
        elif "HARD" in compound_upper:
            compound_color = Color.WHITE
            compound_abbr = "H"
        elif "INTER" in compound_upper:
            compound_color = Color.BLUE
            compound_abbr = "I"
        elif "WET" in compound_upper:
            compound_color = Color.CYAN
            compound_abbr = "W"
        else:
            compound_color = Color.DIM
            compound_abbr = compound[:3] if compound != "N/A" else "N/A"

        print(
            f"{Color.CYAN}{stint_num:<6}{Color.RESET}"
            f"{compound_color}{compound_abbr:<10}{Color.RESET}"
            f"{Color.WHITE}{str(lap_start)[:6]:<7}{str(lap_end)[:6]:<7}{Color.RESET}"
            f"{age_color}{age_display[:7]:<8}{Color.RESET}"
            f"{prog_color}{str(progression)[:7]:<8}{Color.RESET}"
            f"{Color.DIM}{str(total_laps)[:6]:<7}{Color.RESET}"
        )


def show_driver_position(session_key: str, driver_number: str, force_refresh: bool = False):
    """Show position changes for a driver."""
    print_header(f"DRIVER #{driver_number} - POSITION CHANGES")

    positions = fetch_json(
        f"https://api.openf1.org/v1/position?session_key={session_key}&driver_number={driver_number}",
        force_refresh=force_refresh,
    )

    if not positions:
        print(f"{Color.RED}No position data found{Color.RESET}")
        return

    print(
        f"{Color.YELLOW}{Color.BOLD}{'TIME':<12}{'POSITION':<10}{'CHANGE':<10}{Color.RESET}"
    )
    print(f"{Color.DIM}{'─'*32}{Color.RESET}")

    prev_pos = None
    for pos_data in sorted(positions, key=lambda x: x.get("date", "")):
        time = datetime.fromisoformat(pos_data["date"].replace("Z", "+00:00")).strftime(
            "%H:%M:%S"
        )
        position = pos_data.get("position")

        if prev_pos is not None and position is not None:
            change = prev_pos - position
            if change > 0:
                change_str = f"↑ {change}"
                change_color = Color.GREEN
            elif change < 0:
                change_str = f"↓ {abs(change)}"
                change_color = Color.RED
            else:
                change_str = "—"
                change_color = Color.DIM
        else:
            change_str = "—"
            change_color = Color.DIM

        print(
            f"{Color.DIM}{time:<12}{Color.RESET}"
            f"{Color.WHITE}{position:<10}{Color.RESET}"
            f"{change_color}{change_str:<10}{Color.RESET}"
        )

        prev_pos = position


def show_driver_pits(session_key: str, driver_number: str, force_refresh: bool = False):
    """Show pit stops for a driver."""
    print_header(f"DRIVER #{driver_number} - PIT STOPS")

    pits = fetch_json(
        f"https://api.openf1.org/v1/pit?session_key={session_key}&driver_number={driver_number}",
        force_refresh=force_refresh,
    )

    if not pits:
        print(f"{Color.RED}No pit stop data found{Color.RESET}")
        return

    print(f"{Color.YELLOW}{Color.BOLD}{'TIME':<12}{'LAP':<6}{'DURATION':<12}{Color.RESET}")
    print(f"{Color.DIM}{'─'*30}{Color.RESET}")

    for pit in sorted(pits, key=lambda x: x.get("date", "")):
        time = datetime.fromisoformat(pit["date"].replace("Z", "+00:00")).strftime("%H:%M:%S")
        lap = pit.get("lap_number", "N/A")
        duration = pit.get("pit_duration")

        if duration is not None:
            if duration < 3.0:
                duration_color = Color.GREEN + Color.BOLD
            elif duration < 5.0:
                duration_color = Color.GREEN
            else:
                duration_color = Color.YELLOW
            duration_str = f"{duration:.2f}s"
        else:
            duration_color = Color.DIM
            duration_str = "N/A"

        print(
            f"{Color.DIM}{time:<12}{Color.RESET}"
            f"{Color.CYAN}{lap:<6}{Color.RESET}"
            f"{duration_color}{duration_str:<12}{Color.RESET}"
        )


def show_driver_radio(session_key: str, driver_number: str, force_refresh: bool = False):
    """Show team radio for a driver."""
    print_header(f"DRIVER #{driver_number} - TEAM RADIO")

    radios = fetch_json(
        f"https://api.openf1.org/v1/team_radio?session_key={session_key}&driver_number={driver_number}",
        force_refresh=force_refresh,
    )

    if not radios:
        print(f"{Color.RED}No team radio data found{Color.RESET}")
        return

    print(f"{Color.YELLOW}{Color.BOLD}{'TIME':<12}{'RECORDING URL':<60}{Color.RESET}")
    print(f"{Color.DIM}{'─'*72}{Color.RESET}")

    for radio in sorted(radios, key=lambda x: x.get("date", "")):
        time = datetime.fromisoformat(radio["date"].replace("Z", "+00:00")).strftime("%H:%M:%S")
        url = radio.get("recording_url", "N/A")

        print(f"{Color.DIM}{time:<12}{Color.RESET}" f"{Color.CYAN}{url[:59]}{Color.RESET}")


def show_driver_all(session_key: str, driver_number: str, force_refresh: bool = False):
    """Show all available data for a driver."""
    show_driver_laps(session_key, driver_number, force_refresh=force_refresh)
    print()
    show_driver_stints(session_key, driver_number, force_refresh=force_refresh)
    print()
    show_driver_position(session_key, driver_number, force_refresh=force_refresh)
    print()
    show_driver_pits(session_key, driver_number, force_refresh=force_refresh)


def show_current_gp(force_refresh: bool = False):
    """Show current and next Grand Prix using OpenF1."""
    print_header("F1 GRAND PRIX INFO")

    current_year = datetime.now().year

    meetings = fetch_json(
        f"https://api.openf1.org/v1/meetings?year={current_year}",
        force_refresh=force_refresh,
    )

    if not meetings:
        print(f"{Color.RED}No meetings found{Color.RESET}")
        return

    from datetime import timezone

    now = datetime.now(timezone.utc)
    current = None
    next_race = None

    for meeting in meetings:
        meeting_date = datetime.fromisoformat(meeting["date_start"].replace("Z", "+00:00"))
        if meeting_date < now:
            if not current or meeting_date > datetime.fromisoformat(
                current["date_start"].replace("Z", "+00:00")
            ):
                current = meeting
        elif not next_race:
            next_race = meeting

    if current:
        print_section("CURRENT GRAND PRIX")
        print(f"{Color.WHITE}{Color.BOLD}{current['meeting_name']}{Color.RESET}")
        print(f"{Color.YELLOW}🏁 {current['circuit_short_name']}{Color.RESET}")
        print(f"{Color.DIM}📍 {current['location']}, {current['country_name']}{Color.RESET}")
        date_obj = datetime.fromisoformat(current["date_start"].replace("Z", "+00:00"))
        print(f"{Color.GREEN}📅 {date_obj.strftime('%B %d, %Y')}{Color.RESET}")

    print()

    if next_race:
        print_section("NEXT GRAND PRIX")
        print(f"{Color.WHITE}{Color.BOLD}{next_race['meeting_name']}{Color.RESET}")
        print(f"{Color.YELLOW}🏁 {next_race['circuit_short_name']}{Color.RESET}")
        print(f"{Color.DIM}📍 {next_race['location']}, {next_race['country_name']}{Color.RESET}")
        date_obj = datetime.fromisoformat(next_race["date_start"].replace("Z", "+00:00"))
        print(f"{Color.GREEN}📅 {date_obj.strftime('%B %d, %Y')}{Color.RESET}")


def export_data(endpoint: str, params: Dict[str, str], filename: str = None, format: str = "json"):
    """Export data from OpenF1 API in JSON or CSV format."""
    print_header(f"EXPORTING {endpoint.upper()} DATA ({format.upper()})")

    url = f"https://api.openf1.org/v1/{endpoint}"
    if params:
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    print(f"{Color.CYAN}Fetching: {url}{Color.RESET}")
    data = fetch_json(url)

    if not data:
        print(f"{Color.RED}No data to export{Color.RESET}")
        return

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"f1-{endpoint}-{timestamp}.{format}"

    try:
        if format.lower() == "csv":
            export_to_csv(data, endpoint, filename)
        else:
            export_to_json(data, filename)

    except Exception as e:
        print(f"{Color.RED}✗ Export failed: {e}{Color.RESET}")


def export_to_json(data: List[Dict], filename: str):
    """Export data as JSON."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"{Color.GREEN}✓ JSON data exported to: {filename}{Color.RESET}")
    print(f"{Color.DIM}Records: {len(data) if isinstance(data, list) else 1}{Color.RESET}")


def flatten_json(data: Dict, parent_key: str = "", sep: str = "_") -> Dict:
    """Flatten nested JSON/dictionaries for CSV export."""
    items = {}

    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        if isinstance(value, dict):
            items.update(flatten_json(value, new_key, sep=sep))
        elif isinstance(value, list):
            items[new_key] = ", ".join(str(v) for v in value)
        else:
            items[new_key] = value

    return items


def export_to_csv(data: List[Dict], endpoint: str, filename: str):
    """Export data as CSV, handling nested structures."""
    if not data:
        print(f"{Color.RED}No data to export{Color.RESET}")
        return

    flattened_data = []
    for item in data:
        flattened_item = flatten_json(item)
        flattened_data.append(flattened_item)

    fieldnames = set()
    for item in flattened_data:
        fieldnames.update(item.keys())

    fieldnames = sorted(fieldnames)

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in flattened_data:
            row = {field: item.get(field, "") for field in fieldnames}
            writer.writerow(row)

    print(f"{Color.GREEN}✓ CSV data exported to: {filename}{Color.RESET}")
    print(f"{Color.DIM}Records: {len(data)}, Columns: {len(fieldnames)}{Color.RESET}")
    print(
        f"{Color.CYAN}Columns: {', '.join(fieldnames[:5])}..."
        if len(fieldnames) > 5
        else f"{Color.CYAN}Columns: {', '.join(fieldnames)}"
    )


