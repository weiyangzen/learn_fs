# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/check_mkfs.c

Check-framework stub test binary for `main_mkfs.c`.

Behavior:
- Defines one test `test_mkfs_stub` asserting true.
- Builds suite `main_mkfs.c` / case `mkfs.gfs2`.
- Runs tests with `CK_ENV` and returns failure count as process status.

Risk notes:
- No real mkfs functionality is tested here.
