## sources/sync-backup/rsync/testsuite/mkpath_test.py

Purpose: verifies `--mkpath` creates missing destination parent directories for several file and directory destination forms.

Important APIs and control flow: copies source fixtures into `FROMDIR`, changes cwd to `TMPDIR`, and defines `assert_file(path, label, src='from/text')` using `filecmp.cmp`. It first proves a transfer without `--mkpath` fails and creates nothing. It then tests file-to-file deep destination, trailing-slash directory destination, pre-existing destination directory, alternate final filename, whole-directory multi-source with and without trailing slash, and a simple current-directory file destination.

State and dependencies: uses relative paths, `rmtree`, `run_rsync`, `makepath`, and fixture files from `SRCDIR`.

Integration points: covers destination path creation and disambiguation of final component as file versus directory.

Risks and test signals: content comparison for each expected file is strong; negative control ensures the successes are attributable to `--mkpath`.
