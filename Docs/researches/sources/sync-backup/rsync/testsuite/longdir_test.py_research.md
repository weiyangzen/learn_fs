## sources/sync-backup/rsync/testsuite/longdir_test.py

Purpose: regression test for historical path handling bugs with very long directory names.

Important APIs and control flow: calls `hands_setup()`, constructs a 175-character directory name nested three times under `FROMDIR`, creates two leaf files with deterministic content through `make_text_file`, and runs `checkit(['--delete', '-avH', ...], FROMDIR, TODIR)`.

State and dependencies: mutates `FROMDIR` and `TODIR`, requires filesystem support for long path components, and skips if directory or file creation fails.

Integration points: broad transfer, delete, and hard-link logic over long nested paths.

Risks and test signals: platform path length limits are handled via skip. Final `checkit` listing and file diffs prove the long paths survived transfer unchanged.
