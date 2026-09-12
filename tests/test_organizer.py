from pathlib import Path

from file_organizer.organizer import get_category, organize_folder, unique_destination


def test_get_category():
    assert get_category(Path("report.pdf")) == "Documents"
    assert get_category(Path("photo.JPG")) == "Images"
    assert get_category(Path("data.csv")) == "Spreadsheets"
    assert get_category(Path("unknown.xyz")) == "Other"


def test_unique_destination(tmp_path):
    original = tmp_path / "report.pdf"
    original.write_text("existing", encoding="utf-8")

    result = unique_destination(original)

    assert result.name == "report_1.pdf"


def test_organize_folder(tmp_path):
    (tmp_path / "report.pdf").write_text("pdf", encoding="utf-8")
    (tmp_path / "photo.jpg").write_text("image", encoding="utf-8")
    (tmp_path / "notes.xyz").write_text("other", encoding="utf-8")

    stats = organize_folder(tmp_path)

    assert (tmp_path / "Documents" / "report.pdf").exists()
    assert (tmp_path / "Images" / "photo.jpg").exists()
    assert (tmp_path / "Other" / "notes.xyz").exists()

    assert stats == {
        "Documents": 1,
        "Images": 1,
        "Other": 1,
    }


def test_dry_run_does_not_move_files(tmp_path):
    source_file = tmp_path / "report.pdf"
    source_file.write_text("pdf", encoding="utf-8")

    stats = organize_folder(tmp_path, dry_run=True)

    assert source_file.exists()
    assert not (tmp_path / "Documents").exists()
    assert stats == {"Documents": 1}
