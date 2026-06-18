## sources/sync-backup/rsync/testsuite/safe-links_test.py

Purpose: verifies `--safe-links` drops relative symlinks whose literal targets escape the transfer root while preserving in-tree relative symlinks.

Important APIs and control flow: creates `from/safe/files`, `from/safe/links`, and `from/unsafe`. It adds two safe links pointing to `../files/file1` and `../files/file2`, plus two escape attempts using `../../unsafe/unsafefile` and a normalized-upward path. It runs `rsync -avv --safe-links from/safe/ to` and checks safe links exist with exact targets while unsafe links do not exist, including dangling symlink checks.

State and dependencies: changes cwd to `TMPDIR`, uses symlink and path existence helpers.

Integration points: covers symlink safety classification for relative targets and destination omission behavior.

Risks and test signals: symlink support is required. Signals are exact target equality and lexists/islink absence for unsafe names.
