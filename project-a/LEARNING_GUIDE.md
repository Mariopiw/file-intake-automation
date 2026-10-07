# Project A: build, run, understand and publish

## 1. Put the project on your laptop

Download `project-a-complete.zip` into Downloads. In Linux Mint's file manager,
right-click the ZIP and choose Extract Here. It contains a folder `project-a`.
Move that folder to `~/Projects/` using the file manager. If a folder with that
name exists, choose a new name rather than replacing it. The commands below
assume the new project is at `~/Projects/project-a`.

Open Terminal (Ctrl+Alt+T):

```bash
cd ~/Projects/project-a
pwd
ls -a
python3 --version
```

You should see README.md, pyproject.toml, file_organizer, scripts, tests,
LEARNING_GUIDE.md, .gitignore and .github. Python must be at least 3.11.
All exact source code is in this package; no code from a chat screenshot is needed.

## 2. Install in a virtual environment

Run each command separately:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
file-organizer --help
```

If venv is missing, run `sudo apt update` then `sudo apt install python3-venv`.
If your Python is older than 3.11, stop and get help installing a supported
version; do not replace Mint's system Python.

A virtual environment is a toolbox for this project. `activate` selects it.
`pip install -e .` connects the current source folder to the CLI command.
When you edit the source, the editable installation uses those edits.

Offline fallback, from the project folder:

```bash
python3 -m file_organizer.organizer --help
python3 -m unittest discover -s tests -v
```

## 3. Create practice files

```bash
python scripts/make_demo.py
```

It creates four input files and one subfolder. An existing output note exercises
duplicate protection. If demo already exists, the script stops intentionally.
Do not reset it automatically; use a fresh extracted copy for another clean demo.

## 4. Preview before moving

Predict the destinations before running:

```bash
file-organizer --source demo/inbox --destination demo/out --dry-run
```

Expected summary: planned 4, moved 0, skipped 1, errors 0.
The existing output `note.txt` means the new note is planned as `note_1.txt`.
The nested subfolder is skipped. Preview does not change input/output files.

## 5. Apply the plan

```bash
file-organizer --source demo/inbox --destination demo/out --apply --log-file intake.log
```

Expected summary: planned 0, moved 4, skipped 1, errors 0.
Inspect the output and log:

```bash
find demo -maxdepth 3 -type f
cat intake.log
cat demo/out/Documents/note.txt
cat demo/out/Documents/note_1.txt
```

The old note must say `Existing note`; the new one must say `New note`.
Run again:

```bash
file-organizer --source demo/inbox --destination demo/out --dry-run
```

Expected: planned 0, moved 0, skipped 1, errors 0.

## 6. Run the automated checks

```bash
python -m unittest discover -s tests -v
```

There are 17 tests. Every one should pass. Tests use disposable temporary
folders, not your Documents or Downloads. `ERROR` lines within successful CLI
tests are expected: those tests intentionally supply invalid configurations.

## 7. Understand the source

Open `file_organizer/organizer.py` in VS Code or your text editor.

Read in this order:

1. GROUPS and category: the sorting rule.
2. available_name: find a filename that is not already occupied.
3. validate_paths: keep input and output folders separate.
4. organize: look at each direct-child file and preview or process it.
5. verified_move: create a new copy without overwriting, verify and remove source.
6. make_logger: print actions and optionally write a log.
7. main: translate terminal arguments into Python behaviour.

`counts` is a scorecard. `reserved` remembers names chosen in the current run.
The extension is a label, not proof of file contents. `.JPG` is converted to
`.jpg` for matching. SHA-256 is a content fingerprint used to verify the copy.

This version is designed for a trusted local folder. Only use completed files;
do not run multiple organizers or let other programs change them during a run.
Read README's recovery limits before processing important files.

## 8. Publish inside your existing GitHub repository on a branch

This route adds the teaching version as `project-a/` and a separate CI workflow.
It preserves the existing root application. It is not a replacement or merge of
the existing code. You can consolidate the implementations in a later review.

First exit the virtual environment if active:

```bash
deactivate
cd ~/Projects
git clone https://github.com/Mariopiw/file-intake-automation.git file-intake-publish
cd file-intake-publish
git status
git switch -c learning/project-a-complete
```

If the clone directory or branch already exists, stop and inspect it rather than
deleting it. A fresh clone should have a clean working tree.

Create the destination folder; this deliberately fails if it exists:

```bash
mkdir project-a
```

Copy only the deliverable files, excluding .venv, demo files and logs:

```bash
cp ~/Projects/project-a/pyproject.toml project-a/
cp ~/Projects/project-a/README.md project-a/
cp ~/Projects/project-a/LEARNING_GUIDE.md project-a/
cp ~/Projects/project-a/.gitignore project-a/
mkdir project-a/file_organizer project-a/scripts project-a/tests
cp ~/Projects/project-a/file_organizer/*.py project-a/file_organizer/
cp ~/Projects/project-a/scripts/*.py project-a/scripts/
cp ~/Projects/project-a/tests/*.py project-a/tests/
mkdir -p .github/workflows
```

Create `.github/workflows/project-a-ci.yml` in your editor. If it exists already,
review it first. Paste exactly this:

```yaml
name: Project A tests
on: [push, pull_request]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12', '3.13']
    defaults:
      run:
        working-directory: project-a
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: python -m pip install -e .
      - run: python -m unittest discover -s tests -v
      - run: file-organizer --help
```

Test the copied project before committing:

```bash
cd project-a
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
file-organizer --help
cd ..
git status --short
```

Stage specific files:

```bash
git add project-a .github/workflows/project-a-ci.yml
git diff --cached --stat
git diff --cached
```

Check that only intended source, docs, tests and workflow files are staged.
Do not stage real personal files, logs, .env or .venv.

Set your Git name locally if it is not set:

```bash
git config user.name "Mariusz Piwowarczyk"
```

In the command below, replace the placeholder with your verified GitHub email,
or the exact private noreply address shown in GitHub Settings > Emails:

```bash
git config user.email "YOUR_VERIFIED_GITHUB_EMAIL"
```

Do not run it unchanged. Then:

```bash
git commit -m "Add tested Project A teaching implementation"
git push -u origin learning/project-a-complete
```

GitHub account passwords do not authenticate HTTPS Git pushes. Use an already
configured credential manager, GitHub CLI browser authentication, or a suitable
token entered locally when prompted. Never paste a token into chat or a remote
URL. If authentication fails, keep your local commit and request help with the
exact error, excluding secrets.

On GitHub, open your repository > Compare & pull request. Base branch: main;
compare branch: learning/project-a-complete. Describe what was added and include
the local test result. Inspect the Actions checks and Files changed. Merge only
after reviewing the changes and understanding the project. Remote checks have
not run merely because local tests passed.

## 9. Learn actively

For each function: predict behaviour, run it, explain it, change one thing, test.
Study in 45-minute blocks with a short break. Recall the purpose of three
functions tomorrow, in three days and in a week before rereading them.

Exercises:

1. Why is preview the default?
2. Where does a file without an extension go?
3. Why does `note.txt` become `note_1.txt`?
4. Why do we verify before removing the source?
5. Add `.md` to Documents and write a category test before changing GROUPS.
6. Add `.webp` to Images, test it, and explain the change without reading notes.
7. Explain what could happen if a computer crashes during a move.

Answers: preview allows inspection; Other; the original name is occupied;
verification checks the copied bytes; crash recovery is not transactional and
can require manual inspection. Changes 5 and 6 are your independent exercises.

## 10. Explain honestly in an interview

Say you built and studied the project with AI assistance. Demonstrate a dry-run,
duplicate handling, a test and a modification. Explain that this version is for
trusted local files, not malware scanning or concurrent intake. Never claim
production deployment, customers or measured savings unless you have evidence.
