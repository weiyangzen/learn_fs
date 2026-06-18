## sources/sync-backup/rsync/testsuite/metadata-depth_test.py

Purpose: validates permission, mtime, and `--chmod` metadata handling for files and directories at every level of a nested tree.

Important APIs and control flow: `seed()` creates a depth-3 tree, sets all file modes to `0640`, directory modes to `0750`, and distinct old file mtimes. First `run_rsync('-rlpt')` must preserve modes and times. Then a fresh seed with `run_rsync('-a', '--chmod=D710,F600')` must rewrite directory modes to `0710` and file modes to `0600`.

State and dependencies: uses `walk_files`, `walk_dirs`, `assert_mode`, `assert_mtime_close`, and fixed mtimes.

Integration points: covers receiver metadata application over deep parent chains and chmod rule parsing.

Risks and test signals: exact mode assertions are strong. Mtime tolerance accounts for filesystem precision.
