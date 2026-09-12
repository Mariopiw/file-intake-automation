# File Intake Automation

A small Python automation project that organizes files in a folder by file type.

It is intentionally simple, but demonstrates practical automation engineering:

- Python CLI
- filesystem automation
- dry-run safety mode
- logging
- duplicate filename protection
- automated tests
- GitHub Actions CI

## Example

Before:

```text
Downloads/
├── invoice.pdf
├── photo.jpg
├── customers.csv
└── archive.zip
```

After:

```text
Downloads/
├── Archives/
│   └── archive.zip
├── Documents/
│   └── invoice.pdf
├── Images/
│   └── photo.jpg
└── Spreadsheets/
    └── customers.csv
```

## Requirements

- Python 3.11+
- Git

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/file-intake-automation.git
cd file-intake-automation
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project and development dependencies:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Safe test run

Always test with `--dry-run` first:

```bash
file-organizer ~/Downloads --dry-run
```

Nothing is moved.

## Organize files

```bash
file-organizer ~/Downloads
```

## Save a log

```bash
file-organizer ~/Downloads --log-file automation.log
```

## Run tests

```bash
pytest -q
```

Expected result:

```text
4 passed
```

## Portfolio talking point

This project demonstrates a basic automation pipeline:

```text
Input folder
    |
    v
Inspect file extension
    |
    v
Apply classification rule
    |
    v
Create destination
    |
    v
Move file safely
    |
    v
Write log / summary
```

Possible next improvements:

- configurable rules from YAML
- scheduled execution with systemd
- email notifications
- SQLite audit database
- REST API using FastAPI
- Docker container
- malware scanning before moving files
