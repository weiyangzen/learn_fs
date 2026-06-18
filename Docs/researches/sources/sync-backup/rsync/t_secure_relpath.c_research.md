<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/t_secure_relpath.c -->
# sources/sync-backup/rsync/t_secure_relpath.c

Purpose: standalone C test harness for `secure_relative_open()` front-door validation of dangerous relative paths and basedirs containing literal `..` components.

Important APIs/types/functions: `check_relpath()`, `check_basedir()`, and `main()`. It defines required rsync globals and uses `secure_relative_open()`.

Control flow: chdir to a supplied test dir, set daemon/no-chroot globals, create `subdir`, and attempt to open suspect relpaths (`..`, `../foo`, `subdir/..`, `subdir/../subdir`, `foo/../bar`, `/foo`, `/`) and basedirs (`..`, `../subdir`, `subdir/..`, `foo/../bar`). Each check requires failure with `errno == EINVAL`.

State and persistence behavior: creates a `subdir` in the test directory and opens no persistent fd on success because success is treated as failure and closed.

Dependencies and integration points: links with `syscall.c` and test stubs. It exists to keep portable fallback behavior consistent with kernel-enforced resolve-beneath behavior.

Risks: it deliberately rejects paths that may resolve inside the tree after normalization, so callers needing such paths must normalize or rely on the special module-root reanchoring path in `secure_relative_open()`. The test only covers validation, not successful safe opens.

Test signals: every listed path must be rejected with EINVAL. Any valid fd or different errno is reported as a failure and returns nonzero.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/t_secure_relpath.c -->
