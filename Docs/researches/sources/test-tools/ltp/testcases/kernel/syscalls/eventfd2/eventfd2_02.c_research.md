# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/eventfd2_02.c

Purpose: Verifies that `eventfd2()` honors `EFD_NONBLOCK` by setting `O_NONBLOCK` on the open file description.

Important APIs/types/functions: `eventfd2()`, `SAFE_FCNTL(fd, F_GETFL)`, `O_NONBLOCK`, `TST_EXP_EXPR`, and `SAFE_CLOSE`.

Control flow: It creates a descriptor without flags and asserts blocking mode, then creates one with `EFD_NONBLOCK` and asserts nonblocking mode.

State and persistence behavior: Only descriptor status flags are stateful; no counter operations are performed.

Dependencies and integration points: Uses the same local wrapper as other eventfd2 tests and LTP assertion macros.

Risks and test signals: The signal is direct flag inspection, so failures point to eventfd2 flag handling rather than read/write behavior.
