"""Create a disposable sample inbox; refuse to reset an existing demo."""
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "demo"
root.mkdir(exist_ok=False)
inbox = root / "inbox"
inbox.mkdir()
(root / "out" / "Documents").mkdir(parents=True)
(inbox / "note.txt").write_text("New note\n", encoding="utf-8")
(root / "out" / "Documents" / "note.txt").write_text("Existing note\n", encoding="utf-8")
(inbox / "orders.csv").write_text("order_id,quantity\nA001,3\n", encoding="utf-8")
(inbox / "settings.json").write_text('{"sample": true}\n', encoding="utf-8")
(inbox / "unknown.xyz").write_text("Unknown extension\n", encoding="utf-8")
(inbox / "subfolder").mkdir()
(inbox / "subfolder" / "leave.txt").write_text("Not processed\n", encoding="utf-8")
print(f"Demo created at {root}")
