"""Organize a trusted local inbox. Preview is the default."""

import argparse
import hashlib
import logging
import os
from pathlib import Path
import stat
import sys


GROUPS = {
    ".txt": "Documents", ".pdf": "Documents", ".docx": "Documents",
    ".csv": "Data", ".json": "Data", ".xlsx": "Data",
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images",
    ".mp4": "Videos", ".mov": "Videos",
    ".zip": "Archives", ".gz": "Archives",
    ".md": "Documents",
}


def category(path):
    """Use the extension; this does not inspect or validate file contents."""
    return GROUPS.get(path.suffix.lower(), "Other")


def fingerprint(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def available_name(folder, filename, reserved):
    """Avoid existing names, dangling symlinks and earlier preview choices."""
    original = Path(filename)
    candidate = folder / filename
    number = 1
    while os.path.lexists(candidate) or candidate in reserved:
        candidate = folder / f"{original.stem}_{number}{original.suffix}"
        number += 1
    return candidate


def check_folder(path):
    if path.is_symlink():
        raise ValueError(f"Folder must not be a symlink: {path}")
    if path.exists() and not path.is_dir():
        raise ValueError(f"Not a directory: {path}")


def validate_paths(source, destination):
    check_folder(source)
    check_folder(destination)
    source = source.resolve(strict=True)
    destination = destination.resolve()
    if not source.is_dir():
        raise ValueError("Source must be a directory")
    if (source == destination or source in destination.parents
            or destination in source.parents):
        raise ValueError("Source and destination must be separate, non-nested folders")
    return source, destination


def verified_move(source, target):
    """Create exclusively, verify bytes, then remove source.

    Use a trusted inbox with no concurrent writers. This is not a transaction
    or a defence against hostile directory changes.
    """
    before = source.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError("Source is no longer a regular file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(source, flags)
    created = False
    try:
        with os.fdopen(descriptor, "rb") as reader:
            if fingerprint(os.fstat(reader.fileno())) != fingerprint(before):
                raise ValueError("Source changed before copying")
            digest = hashlib.sha256()
            # 'xb' fails if the destination name already exists; no overwrite.
            with target.open("xb") as writer:
                created = True
                for chunk in iter(lambda: reader.read(1024 * 1024), b""):
                    writer.write(chunk)
                    digest.update(chunk)
                writer.flush()
                os.fsync(writer.fileno())
            if fingerprint(source.lstat()) != fingerprint(before):
                raise ValueError("Source changed while copying")
            if checksum(target) != digest.hexdigest():
                raise ValueError("Destination checksum verification failed")
    except BaseException:
        if created:
            target.unlink(missing_ok=True)
        raise
    # If unlink fails, both complete copies remain and the run reports failure.
    source.unlink()


def organize(source, destination, apply=False, logger=None):
    logger = logger or logging.getLogger("file-organizer")
    source, destination = validate_paths(Path(source), Path(destination))
    counts = {"planned": 0, "moved": 0, "skipped": 0, "errors": 0}
    reserved = set()
    # Snapshot the direct children only. Never recurse into directories.
    items = sorted(source.iterdir(), key=lambda item: item.name)
    for item in items:
        try:
            if item.is_symlink() or not item.is_file():
                counts["skipped"] += 1
                logger.info("SKIP %r (folder, symlink or special file)", item.name)
                continue
            folder = destination / category(item)
            check_folder(folder)
            target = available_name(folder, item.name, reserved)
            reserved.add(target)
            if apply:
                folder.mkdir(parents=True, exist_ok=True)
                verified_move(item, target)
                counts["moved"] += 1
                logger.info("MOVED %r -> %r", str(item), str(target))
            else:
                counts["planned"] += 1
                logger.info("PLAN %r -> %r", str(item), str(target))
        except (OSError, ValueError) as error:
            counts["errors"] += 1
            logger.error("ERROR %r: %s", item.name, error)
    return counts


def make_logger(log_file=None):
    logger = logging.getLogger("file-organizer")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    logger.addHandler(console)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(file_handler)
    return logger


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Actually move files")
    mode.add_argument("--dry-run", action="store_true", help="Preview (also the default)")
    parser.add_argument("--log-file", type=Path, help="Existing parent folder required")
    args = parser.parse_args(argv)
    logger = make_logger()
    try:
        source, destination = validate_paths(args.source, args.destination)
        if args.log_file:
            log_path = args.log_file.expanduser().resolve()
            if log_path == source or source in log_path.parents:
                raise ValueError("Log file must be outside the source folder")
            if log_path == destination or destination in log_path.parents:
                raise ValueError("Log file must be outside the destination folder")
            logger = make_logger(log_path)
        counts = organize(source, destination, apply=args.apply, logger=logger)
        logger.info("SUMMARY %s", counts)
        return 1 if counts["errors"] else 0
    except (OSError, ValueError) as error:
        logger.error("%s", error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
