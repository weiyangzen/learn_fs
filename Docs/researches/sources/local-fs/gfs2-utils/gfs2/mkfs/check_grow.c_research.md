# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/check_grow.c

Check-framework stub test binary for `main_grow.c`.

Behavior:
- Defines one test `test_grow_stub` asserting true.
- Builds suite `main_grow.c` / case `grow.gfs2`.
- Runs tests with `CK_ENV` and returns failure count as process status.

Risk notes:
- Provides build/test harness coverage only; no behavioral assertions for grow logic.
