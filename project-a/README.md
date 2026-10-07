# File Intake Automation — Project A

A Python CLI for organizing a trusted local inbox into extension-based folders.
Author: Mariusz Piwowarczyk. Python 3.11+. No third-party runtime dependencies.

This is a standalone teaching implementation. It has not been merged into the
existing GitHub repository or verified against that repository's current code.

## Current features

- Preview by default; `--apply` explicitly enables moves.
- Direct-child files only. Folders, symlinks and special files are skipped.
- Extension groups: Documents, Data, Images, Videos, Archives, Other.
- Duplicate filename protection (`note.txt`, `note_1.txt`, ...).
- Exclusive destination creation, SHA-256 copy verification, source-change checks.
- Per-file error handling, console output and optional file logging.
- Automated tests and GitHub Actions CI configuration.
- Exit status 0 for success, 1 for processing/configuration failure, 2 for CLI usage errors.

## Install on Linux Mint

Open a terminal inside this project directory:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
file-organizer --help
```

Python must be 3.11 or newer. If venv is missing, install `python3-venv` with your
system package manager. Installing the package needs setuptools and may access
PyPI. You can run the module and tests without installing anything:

```bash
python3 -m file_organizer.organizer --help
python3 -m unittest discover -s tests -v
```

## Demonstration

```bash
python scripts/make_demo.py
file-organizer --source demo/inbox --destination demo/out --dry-run
file-organizer --source demo/inbox --destination demo/out --apply --log-file intake.log
file-organizer --source demo/inbox --destination demo/out --dry-run
```

The script refuses to replace an existing demo. Start with a fresh extracted
project for a clean demo. Expected first preview: 4 planned, 1 skipped, 0 errors.
Expected apply: 4 moved, 1 skipped, 0 errors. Existing `note.txt` is preserved;
new note becomes `Documents/note_1.txt`. Final preview: 0 planned, 1 skipped.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests cover previews, byte preservation, collisions, symlinks, nested paths,
checksum failures, existing destinations, per-file failures, CLI and logging.
GitHub Actions runs tests on Python 3.11, 3.12 and 3.13. Local results do not
establish that remote GitHub CI has run.

## Operational limits

Use a dedicated inbox containing completed files, with one organizer process
and no other process writing or renaming these files. This is not a sandbox for
hostile users or an atomic transactional move system. Classification uses the
extension only; it is not malware scanning or content validation. File metadata
(permissions, modification times, extended attributes) is not preserved.

A crash between copying and deletion can leave both copies, or an incomplete
destination if interrupted during copying. If source deletion fails, a verified
destination remains and an error is reported. Stop and inspect both paths before
retrying such a failure; retrying can create a suffixed copy. Logs contain paths.
Dry-run makes no intake/output changes, but an explicitly requested log is written.

## Future improvements

YAML rules, scheduling/systemd, email notifications, SQLite audit history,
FastAPI, Docker, malware scanning, transactional recovery and concurrency control.
These are not current features.

See `LEARNING_GUIDE.md` for exact setup, GitHub commands and exercises.
