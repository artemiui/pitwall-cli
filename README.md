# Pitwall CLI
# Pitwall-CLI

Pitwall-CLI is an interactive command-line viewer for Formula 1 data powered by the OpenF1 API. It was created to make exporting and exploring F1 data easier for analysts and fans who want quick access to structured results, laps, stints, and telemetry-derived endpoints without writing API calls manually.


![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)


## Features
- Interactive prompt with contextual breadcrumbs and colorized output.
- Quick navigation: enter a year, meeting key, session key, or driver number to drill down.
- Driver data views: laps, stints, position changes, pit stops, team radio, or “all”.
- Exports: any OpenF1 endpoint to JSON (default) or CSV with automatic context filling.
- Smart caching with expiry per endpoint and controls to clear or inspect cache.
- Retry-aware HTTP client with basic rate-limit messaging.

## Commands (interactive mode)
- `year` (e.g., `2024`): list all Grand Prix for that season.
- `meeting_key` (number): list sessions for that Grand Prix.
- `session_key` (number): list drivers and rankings for that session.
- `driver_number` (number): open driver data menu.
- Driver data within a session/driver: `laps`, `stints`, `position`, `pit`, `radio`, `all`.
- `gp` or `current`: show current and next Grand Prix.
- `export <endpoint> [format=csv|json] [key=value ...]`: export data. Context (year/session/driver) auto-fills missing params when available.
- `cache <stats|clear|info>`: inspect or clear cached API responses.
- `refresh`: bypass cache for the current view and refetch.
- `context` / `where`: show current navigation state.
- `clear`: clear the screen and re-render the current view.
- `back`: go up one level; `help`: show help; `exit|quit|q`: leave interactive mode.

## Examples
- `2025` → list 2025 Grand Prix.
- `1254` (after a year) → show sessions for that event.
- `9636` (after selecting a meeting) → show session drivers.
- `44` (after selecting a session) → open driver #44 menu.
- `laps` (within driver context) → show lap times.
- `export laps format=csv` → export current session & driver lap data to CSV using context.
- `export meetings format=csv year=2024` → export all 2024 meetings.

## Installation
1) Use Python 3.10+.
2) Install dependencies:
```
pip install -r requirements.txt
```

## Running
- Interactive mode (recommended):  
```
python main.py
```
- One-off command:  
```
python main.py 2024
python main.py export laps format=csv session_key=9636 driver_number=44
```

## Data exports
- Defaults to JSON; add `format=csv` for CSV.
- If you’re already in a session/driver context, missing params are auto-filled (e.g., current `session_key` or `driver_number`).
- Files save to the current working directory with timestamped names unless you specify `filename` when calling `export_data` programmatically.

## Caching
- Cached per-endpoint with sensible expirations (sessions/meetings daily, laps/stints hourly, position every 30 minutes, default 6 hours).
- Manage via `cache clear [endpoint]`, `cache stats`, or `cache info`.
- Use `refresh` to bypass cache for the current view.

## Testing
Run the test suite with:
```
pytest
```

## Notes
- API source: [OpenF1](https://openf1.org/).
- Exported CSVs include flattened nested fields to simplify downstream analysis.
A simple command-line interface for accessing and exporting real-time and historical F1 data from the OpenF1 API. Made for easier access to F1 data ready for analytics.

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## Features

- **Navigation**: Hierarchical browsing from seasons to individual driver telemetry
- **Export Formats**: Export data as JSON or CSV for analysis
- **Rich Terminal Interface**: Color-coded output with intuitive navigation
- **Data Coverage**: Sessions, drivers, laps, stints, positions, pit stops, and more
- **Intelligent Caching**: Automatic local caching with smart expiration policies

## Installation
### Install from Source
```bash
git clone https://github.com/artemiui/pitwall-cli.git
cd pitwall-cli
pip install -r requirements.txt
```

### Dependencies
```bash
pip install requests pandas  # Core dependencies
```

## 🚀 Quick Start

### Interactive Mode
```bash
# Start the interactive CLI
python f13.py

# Or after installation:
fastlap
```

### Single Command Mode
```bash
# View current and next Grand Prix
python f13.py gp

# Browse the 2024 season
python main.py 2024

# Export driver lap times as CSV
python f13.py export laps format=csv session_key=9636 driver_number=44
```

## 📖 Usage Guide

### Navigation Flow
The CLI follows a natural hierarchical navigation:

```mermaid
flowchart LR
    A[Year] --> B[Grand Prix<br>Meeting]
    B --> C[Session<br>Practice/Qualifying/Race]
    C --> D[Driver]
    D --> E[Data<br>Laps/Stints/Pit Stops]
```

### Interactive Navigation
```
f1> 2024                     # Browse 2024 season
f1/2024> 1056                # Select Australian Grand Prix
f1/meeting-1056> 9636        # Select Race session
f1/session-9636> 44          # Select driver #44 (Hamilton)
f1/driver-44> laps           # View lap times
f1/driver-44> back           # Go back to driver list
```

### Command Reference

#### Core Navigation
| Command | Description | Example |
|---------|-------------|---------|
| `[year]` | Browse a specific season | `2024` |
| `[meeting_key]` | Select a Grand Prix | `1056` |
| `[session_key]` | Select a session | `9636` |
| `[driver_number]` | Select a driver | `44` |
| `back` | Navigate back one level | `back` |
| `gp` / `current` | Show current/next Grand Prix | `gp` |

#### Driver Data Commands
| Command | Description | Example |
|---------|-------------|---------|
| `laps` | Lap times and sector data | `laps` |
| `stints` | Tyre stint information | `stints` |
| `position` | Position changes during session | `position` |
| `pit` | Pit stop data | `pit` |
| `radio` | Team radio messages | `radio` |
| `all` | Show all available driver data | `all` |

#### Data Export
```bash
# Export current context data as CSV
export laps format=csv

# Export specific data with parameters
export stints format=csv session_key=9636 driver_number=44

# Export meetings for a year
export meetings format=csv year=2024

# Export as JSON (default)
export laps session_key=9636
```

#### Cache Management
```bash
# Show cache statistics
cache stats

# Clear all cached data
cache clear

# Clear specific endpoint cache
cache clear sessions

# Force refresh current view
refresh
```

#### Utility Commands
| Command | Description |
|---------|-------------|
| `help` | Show help menu |
| `context` / `where` | Show current navigation context |
| `clear` | Clear screen and refresh view |
| `exit` / `quit` / `q` | Exit the application |

## 📊 Data Examples

### Lap Time Display
```
DRIVER #44 - LAP TIMES
─────────────────────────────────────────────────────
LAP   TIME         S1        S2        S3      SPEED
─────────────────────────────────────────────────────
1     98.123s     32.456s   33.123s   32.544s  312 km/h
2     97.845s     32.123s   32.987s   32.735s  315 km/h
3     97.234s     31.987s   32.456s   32.791s  318 km/h
```

### Tyre Stint Analysis
```
DRIVER #44 - TYRE STINTS
─────────────────────────────────────────────────────
STINT  COMPOUND    START    END    PROG.    TOTAL
─────────────────────────────────────────────────────
1      SOFT        1        22     22 laps  (22)
2      MEDIUM      23       42     20 laps  (20)  
3      SOFT        43       58     16 laps  (16)
```

## ⚙️ Configuration

### Cache Settings
The CLI automatically caches data in `~/.f1cli_cache/` with intelligent expiration:

| Data Type | Cache Duration | Purpose |
|-----------|----------------|---------|
| Meetings | 24 hours | Grand Prix schedules rarely change |
| Sessions | 24 hours | Session lists are stable |
| Driver Info | 12 hours | Driver details per session |
| Lap Data | 1 hour | Lap times could be updated |
| Position Data | 30 minutes | Real-time positions |

### Environment Variables
```bash
# Increase timeout for slow connections
export F1_REQUEST_TIMEOUT=15

# Disable caching for development
export F1_DISABLE_CACHE=1

# Set custom cache directory
export F1_CACHE_DIR=~/.my_f1_cache
```

## 🔧 Development
### Key Components
- **F1Cache Class**: Intelligent caching with expiration policies
- **Context Management**: Track navigation state across commands
- **fetch_json()**: Robust HTTP client with retry logic
- **Color System**: ANSI color codes for rich terminal output
### Extending the CLI
To add a new data endpoint:
1. Add a new function:
```python
def show_driver_weather(session_key: str, driver_number: str, force_refresh: bool = False):
    url = f"https://api.openf1.org/v1/weather?session_key={session_key}"
    # ... implementation
```
2. Add to driver menu options
3. Add command handler in `process_command()`
## 🤝 Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
### Development Setup
```bash
# Clone and setup
git clone https://github.com/yourusername/fastlap-cli.git
cd fastlap-cli
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Format code
black f13.py
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: `Read timed out (read timeout=5)`
**Solution**: The CLI automatically retries with exponential backoff. For persistent issues:
```bash
# Use the refresh command to bypass cache
refresh
```

**Issue**: No data returned for session
**Solution**: Some historical sessions may have limited data. Try:
- Checking the OpenF1 API directly: `https://api.openf1.org/v1/sessions?year=2024`
- Using a different session key

**Issue**: Colors not displaying correctly
**Solution**: Ensure your terminal supports ANSI colors. Disable colors with:
```bash
export NO_COLOR=1
```

### Debug Mode
```bash
# Enable debug logging
export F1_DEBUG=1
python f13.py 2024
```

## 📈 Performance
- **First load**: 2-5 seconds (API fetch + cache)
- **Cached load**: < 0.1 seconds (local cache)
- **Memory usage**: < 50MB
- **Cache size**: Typically 10-50MB per season

## 🔗 API Reference

This CLI uses the [OpenF1 API](https://api.openf1.org), which provides:
- Free access to historical F1 data
- Real-time data during live sessions
- Comprehensive endpoints for all F1 data types

### Rate Limiting
The OpenF1 API has rate limits for unauthenticated access:
- Free tier: Limited requests per minute
- Paid tier: Higher limits available
This CLI includes automatic rate limit detection and exponential backoff.

## Acknowledgments

- [OpenF1](https://api.openf1.org) for providing such a comprehensive, useful API without need for imports
