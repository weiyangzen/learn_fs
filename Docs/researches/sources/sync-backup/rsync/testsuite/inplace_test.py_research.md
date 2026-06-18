## sources/sync-backup/rsync/testsuite/inplace_test.py

Purpose: verifies `--inplace` updates a deep destination file without replacing its inode, while the default temp-and-rename path does replace it.

Important APIs and control flow: `seed()` builds a depth-3 data tree; `inode()` returns `st_ino`; `modify_deep()` flips bytes in the middle of the source file and bumps mtime to force a delta. The first phase syncs, records inode, runs `--inplace --no-whole-file`, checks content and same inode. The control phase syncs fresh, runs default `--no-whole-file`, and requires a different inode.

State and dependencies: uses data files, mtimes, and inode observations in `FROMDIR`/`TODIR`.

Integration points: covers receiver update strategy, temporary file rename behavior, and deep path resolution.

Risks and test signals: inode equality is filesystem-sensitive but appropriate for local POSIX tests. Content equality guards against a no-op or corrupt update.
