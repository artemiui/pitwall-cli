"""Navigation context shared across the CLI."""


class Context:
    current_year = None
    current_meeting_key = None
    current_session_key = None
    current_driver = None
    meetings_cache = []
    sessions_cache = []


