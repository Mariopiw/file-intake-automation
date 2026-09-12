from __future__ import annotations

import argparse
import logging
import shutil
from pathlib import Path

CATEGORY_MAP = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf"},
    "Spreadsheets": {".csv", ".xls", ".xlsx", ".ods"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".json", ".yaml", ".yml"},
}

logger = logging.getLogger(__name__)


def configure_logging(log_file: Path | None = None, verbose: bool = False) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=handlers,
        force=True,
    )


def get_category(file_path: Path) -> str:
    extension = file_path.suffix.lower()

    for category, extensions in CATEGORY_MAP.items():
        if extension in extensions:
            return category

    return "Other"


def unique_destination(destination: Path) -> Path:
    if not destination.exists():
        return destination

    counter = 1
    while True:
        candidate = destination.with_name(
            f"{destination.stem}_{counter}{destination.suffix}"
        )
        if not candidate.exists():
            return candidate
        counter += 1


def organize_folder(source: Path, dry_run: bool = False) -> dict[str, int]:
    if not source.exists():
        raise FileNotFoundError(f"Folder does not exist: {source}")

    if not source.is_dir():
        raise NotADirectoryError(f"Not a directory: {source}")

    stats: dict[str, int] = {}
    files = [item for item in source.iterdir() if item.is_file()]

    if not files:
        logger.info("No files found in %s", source)
        return stats

    for file_path in files:
        category = get_category(file_path)
        category_dir = source / category
        destination = unique_destination(category_dir / file_path.name)

        logger.info(
            "%s %s -> %s",
            "[DRY RUN]" if dry_run else "MOVE",
            file_path.name,
            destination,
        )

        if not dry_run:
            category_dir.mkdir(exist_ok=True)
            shutil.move(str(file_path), str(destination))

        stats[category] = stats.get(category, 0) + 1

    return stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Automatically organize files into category folders."
    )
    parser.add_argument(
        "folder",
        type=Path,
        help="Folder to organize, for example ~/Downloads",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned moves without changing files.",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Optional log file path.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    configure_logging(args.log_file, args.verbose)

    try:
        stats = organize_folder(args.folder.expanduser().resolve(), args.dry_run)
    except (FileNotFoundError, NotADirectoryError) as exc:
        parser.error(str(exc))

    if stats:
        summary = ", ".join(
            f"{category}: {count}"
            for category, count in sorted(stats.items())
        )
        logger.info("Finished. %s", summary)
    else:
        logger.info("Finished. Nothing to organize.")


if __name__ == "__main__":
    main()
