# File Intake Automation

A Python command-line tool that organizes files into folders by extension, with a preview mode before changes are made.

## Key features

- File classification and safe naming of duplicate files
- Dry-run preview and optional logging
- Automated tests

## Quick start

Requires Python 3.11+.

```bash
git clone https://github.com/Mariopiw/file-intake-automation.git
cd file-intake-automation
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
file-organizer ~/Downloads --dry-run
```

After reviewing the preview, run `file-organizer ~/Downloads` to move files.

## Tests

```bash
pytest -q
```

**Scope:** Organizes files by extension; it does not inspect file contents or scan for malware. Try it on a disposable test directory before using important files.
