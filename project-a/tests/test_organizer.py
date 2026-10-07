import logging
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from file_organizer.organizer import category, main, organize, verified_move


class OrganizerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "inbox"
        self.source.mkdir()
        self.out = self.root / "out"
        self.logger = logging.getLogger("test-organizer")
        self.logger.addHandler(logging.NullHandler())
        self.logger.propagate = False

    def run_tool(self, apply=False):
        return organize(self.source, self.out, apply=apply, logger=self.logger)

    def test_category_case_and_unknown(self):
        self.assertEqual(category(Path("PHOTO.JPG")), "Images")
        self.assertEqual(category(Path("no_extension")), "Other")
        self.assertEqual(category(Path("lesson.md")), "Documents")

    def test_preview_does_not_change_files_or_create_output(self):
        file = self.source / "note.txt"
        file.write_text("hello")
        result = self.run_tool()
        self.assertEqual(result["planned"], 1)
        self.assertEqual(file.read_text(), "hello")
        self.assertFalse(self.out.exists())

    def test_move_preserves_binary_bytes(self):
        file = self.source / "PHOTO.JPG"
        data = bytes(range(256)) * 100
        file.write_bytes(data)
        result = self.run_tool(apply=True)
        self.assertEqual(result["moved"], 1)
        self.assertEqual((self.out / "Images" / file.name).read_bytes(), data)
        self.assertFalse(file.exists())

    def test_collision_preserves_original_and_uses_next_suffix(self):
        folder = self.out / "Documents"
        folder.mkdir(parents=True)
        (folder / "note.txt").write_text("old")
        (folder / "note_1.txt").write_text("older")
        (self.source / "note.txt").write_text("new")
        self.run_tool(apply=True)
        self.assertEqual((folder / "note.txt").read_text(), "old")
        self.assertEqual((folder / "note_1.txt").read_text(), "older")
        self.assertEqual((folder / "note_2.txt").read_text(), "new")

    def test_empty_folder(self):
        self.assertEqual(self.run_tool(), {"planned": 0, "moved": 0, "skipped": 0, "errors": 0})

    def test_skip_directory_and_symlink(self):
        (self.source / "nested").mkdir()
        outside = self.root / "outside.txt"
        outside.write_text("leave me")
        (self.source / "link.txt").symlink_to(outside)
        result = self.run_tool(apply=True)
        self.assertEqual(result["skipped"], 2)
        self.assertEqual(outside.read_text(), "leave me")

    def test_dangling_destination_symlink_is_not_overwritten(self):
        folder = self.out / "Documents"
        folder.mkdir(parents=True)
        link = folder / "note.txt"
        link.symlink_to(self.root / "missing")
        (self.source / "note.txt").write_text("new")
        self.run_tool(apply=True)
        self.assertTrue(link.is_symlink())
        self.assertEqual((folder / "note_1.txt").read_text(), "new")

    def test_reject_nested_folders(self):
        with self.assertRaises(ValueError):
            organize(self.source, self.source / "out")
        with self.assertRaises(ValueError):
            organize(self.source, self.root)

    def test_reject_symlink_category(self):
        self.out.mkdir()
        outside = self.root / "external"
        outside.mkdir()
        (self.out / "Documents").symlink_to(outside, target_is_directory=True)
        (self.source / "note.txt").write_text("new")
        result = self.run_tool(apply=True)
        self.assertEqual(result["errors"], 1)
        self.assertTrue((self.source / "note.txt").exists())
        self.assertEqual(list(outside.iterdir()), [])

    def test_second_run_moves_nothing(self):
        (self.source / "note.txt").write_text("new")
        self.run_tool(apply=True)
        self.assertEqual(self.run_tool(apply=True)["moved"], 0)

    def test_checksum_failure_preserves_source_and_removes_copy(self):
        source = self.source / "note.txt"
        target = self.root / "target.txt"
        source.write_text("new")
        with patch("file_organizer.organizer.checksum", return_value="wrong"):
            with self.assertRaises(ValueError):
                verified_move(source, target)
        self.assertEqual(source.read_text(), "new")
        self.assertFalse(target.exists())

    def test_destination_create_failure_preserves_existing_file(self):
        source = self.source / "note.txt"
        target = self.root / "target.txt"
        source.write_text("new")
        target.write_text("old")
        with self.assertRaises(FileExistsError):
            verified_move(source, target)
        self.assertEqual(source.read_text(), "new")
        self.assertEqual(target.read_text(), "old")

    def test_per_file_error_does_not_stop_other_files(self):
        (self.source / "bad.txt").write_text("bad")
        (self.source / "good.csv").write_text("good")
        original = verified_move
        def fail_one(source, target):
            if source.name == "bad.txt":
                raise PermissionError("simulated permission failure")
            return original(source, target)
        with patch("file_organizer.organizer.verified_move", side_effect=fail_one):
            result = self.run_tool(apply=True)
        self.assertEqual(result["errors"], 1)
        self.assertEqual(result["moved"], 1)
        self.assertTrue((self.source / "bad.txt").exists())

    def test_cli_default_is_preview(self):
        (self.source / "note.txt").write_text("new")
        self.assertEqual(main(["--source", str(self.source), "--destination", str(self.out)]), 0)
        self.assertTrue((self.source / "note.txt").exists())

    def test_cli_missing_source_returns_error(self):
        self.assertEqual(main(["--source", str(self.root / "missing"),
                               "--destination", str(self.out)]), 1)

    def test_log_file_outside_inbox(self):
        log = self.root / "run.log"
        (self.source / "note.txt").write_text("new")
        self.assertEqual(main(["--source", str(self.source), "--destination", str(self.out),
                               "--log-file", str(log)]), 0)
        self.assertIn("PLAN", log.read_text())
        self.assertIn("SUMMARY", log.read_text())

    def test_reject_log_in_source(self):
        self.assertEqual(main(["--source", str(self.source), "--destination", str(self.out),
                               "--log-file", str(self.source / "run.log")]), 1)
        self.assertFalse((self.source / "run.log").exists())


if __name__ == "__main__":
    unittest.main()
