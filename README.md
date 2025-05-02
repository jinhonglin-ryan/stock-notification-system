# Stock Notification System

A notification system for tracking and alerting on stock price movements.

## Development

This project uses UV for package management.

### Setup Development Environment

```bash
# Install uv globally
pip install uv

# Setup project
uv sync --all-extras --dev

# Activate virtual environment
source .venv/bin/activate
```

### Documentation

Build documentation locally:

```bash
uv run mkdocs build
```

Serve documentation locally:

```bash
uv run mkdocs serve
```

Documentation will automatically deploy to GitHub Pages when changes are merged to the main branch. 