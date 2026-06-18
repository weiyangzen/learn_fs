## sources/sync-backup/rsync/testsuite/dir-sgid_test.py

Purpose: verifies rsync respects a setgid destination parent when creating new destination directories outside the transferred tree.

Important APIs and control flow: imports `SCRATCHDIR`, `run_rsync`, `check_perms`, `test_fail`, and `test_skipped`. It sets umask to `077`, discovers a secondary group when available, and defines `testit(dirname, dirperms, file_expected, prog_expected, dir_expected, setgid)`. `testit()` creates a parent destination, optionally changes its group, applies integer or symbolic permissions, runs `rsync -rvv` with a source directory, regular file, and program into `todir/to/`, then checks modes and setgid group inheritance.

State and dependencies: creates scratch source entries and two destination parents. It mutates process umask and restores it at the end. It uses `chmod` and optionally `getfacl`; default ACLs on Cygwin cause a skip.

Integration points: covers permission and gid propagation in receiver-side directory creation when rsync creates missing parent components rather than transferring them directly.

Risks and test signals: test is sensitive to filesystem setgid semantics and OS group inheritance differences, so it only asserts the portable setgid case. Signals are exact mode strings and gid equality for `to` and `to/dir`.
