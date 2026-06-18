# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/eventfd2.h

Purpose: Provides a small LTP-local wrapper for invoking the raw `eventfd2` syscall by number.

Important APIs/types/functions: `tst_syscall(__NR_eventfd2, count, flags)`, `lapi/syscalls.h`, `tst_brk(TBROK | TERRNO)`, and an inline `eventfd2()` helper.

Control flow: The helper calls the syscall and aborts the test on `-1`; otherwise it returns the new file descriptor to callers.

State and persistence behavior: No persistent state is stored in the header. It centralizes syscall invocation and error policy for all eventfd2 tests.

Dependencies and integration points: Used by `eventfd2_01.c`, `_02.c`, and `_03.c` to avoid depending on libc exporting `eventfd2()` directly.

Risks and test signals: Because the wrapper breaks on any syscall failure, tests that need to assert negative `eventfd2` behavior would require a different helper. Current users only test successful creation and flags.
