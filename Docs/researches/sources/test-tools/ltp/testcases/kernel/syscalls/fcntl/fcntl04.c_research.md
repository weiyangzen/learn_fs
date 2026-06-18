# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl04.c

Purpose: basic `F_GETFL` test verifying file status flags can be queried and preserve the `O_RDWR` access mode.

Important APIs/types/functions: `fcntl(fd, F_GETFL, 0)`, `O_ACCMODE`, `O_RDWR`, `SAFE_OPEN`, `SAFE_CLOSE`, and LTP `TEST`.

Control flow: setup opens a temp file `O_RDWR | O_CREAT`. The test calls `F_GETFL`, fails on `-1`, then masks `O_ACCMODE` and requires `O_RDWR`.

State/persistence behavior: one open fd; no file status flags are changed.

Dependencies/integration: modern LTP tempdir harness.

Risks/test signals: passing requires only access-mode correctness. Other status flags are tolerated.
