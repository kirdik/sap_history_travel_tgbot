# GeoBot - AGENTS.md

This file contains guidelines for agentic coding agents working on this repository.

## Build/Lint/Test Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running the bot
```bash
# With polling (for testing)
python bot/main.py

# With webhook (for production)
python bot/main.py
```

### Running tests
No tests are currently configured in this project.

## Code Style Guidelines

### Project Structure
This is a Telegram bot for tracking paddleboard trips using GPX tracks.

### Technology Stack
- **aiogram 3.x** - Async Telegram bot framework
- **gpxpy** - GPX file parsing
- **matplotlib** + **Pillow** - Graphics generation
- **sqlite3** - Database (Python built-in)

### Code Style
- Use type hints for function parameters and return values
- Use dataclasses for models (`Trip`, `Media`)
- Follow PEP 8 naming conventions (snake_case for functions/variables)
- Async/await for all I/O operations
- Russian language for user-facing text
- English for code comments and documentation

### Imports
- Group imports: standard library, third-party, local modules
- Use absolute imports within the project
- Example:
  ```python
  import logging
  import os
  from aiogram import Router, types
  from bot.services.gpx_parser import parse_gpx
  ```

### Error Handling
- Use try/except blocks for user input handling
- Log errors with `logger.error()`
- Provide user-friendly error messages
- Never expose sensitive data in error messages

### Database
- SQLite via `database.db` singleton
- All DB operations in `database/db.py`
- Models in `bot/models/` using dataclasses
- Use parameterized queries to prevent SQL injection

### FSM (Finite State Machine)
- Define states in each handler file
- Use `MemoryStorage` for state management
- Always clear state after completion
- State classes end with `StatesGroup`

### Callback Data Format
- Use prefix-based patterns: `<entity>_<action>_<id>`
- Examples: `trip_page_1`, `trip_view_5`, `trip_addmedia_10`
- Keep callback data under 64 bytes

### File Paths
- Store paths in `config.py`: `TRACKS_DIR`, `MEDIA_DIR`, `GRAPHICS_DIR`
- Use `os.path.join()` for path construction
- Always create directories with `os.makedirs(..., exist_ok=True)`

### Graphics
- Use matplotlib with Russian font support (`DejaVu Sans`)
- Graphics saved as PNG to `GRAPHICS_DIR`
- Naming: `trip_<date>.png`

### Handler Organization
- One file per feature: `track.py`, `media.py`, `list.py`, `view.py`, `edit.py`, `delete.py`, `stats.py`
- Router pattern: `router = Router()`
- Check `ADMIN_ID` at the start of handlers
- Always return early if user is not admin

### Configuration
- All config in `config.py`
- Use `.env` file for secrets
- Required vars: `ADMIN_ID`, `BOT_TOKEN`
- Optional vars: `WEBHOOK_URL`, `WEBHOOK_PATH`

### Important Notes
- Bot is single-user (ADMIN_ID check in every handler)
- No authentication system - hard-coded admin only
- Simple, focused functionality
- Media files are stored locally
- Graphics generated on-demand
