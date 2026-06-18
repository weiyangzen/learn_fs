# sources/test-tools/strace/tests/sockname.c

Purpose: Standalone or shared strace regression test for socket address/option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `test_sockname_syscall`. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`. Preprocessor knobs/macros are `TEST_SYSCALL_STR=STRINGIFY_VAL(TEST_SYSCALL_NAME)`, `TEST_SOCKET=TEST_SYSCALL_STR ".socket"`, `PREPARE_TEST_SYSCALL_INVOCATION=do { TEST_SYSCALL_PREPARE; } while (0)`, `PREPARE_TEST_SYSCALL_INVOCATION=do {} while (0)`, `PREFIX_S_ARGS`, `PREFIX_F_ARGS`, `PREFIX_S_STR=""`, `PREFIX_F_STR=""`, `SUFFIX_ARGS`, `SUFFIX_STR=""`. The file has 153 source lines and was read from `sources/test-tools/strace/tests/sockname.c`.

Control flow: `main` and helpers (`test_sockname_syscall`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 4 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: tail-allocated memory creates readable and faulting boundary cases; child process state is synchronized with wait/signal helpers.

Dependencies: Direct dependencies are `tests.h`, `stddef.h`, `stdio.h`, `string.h`, `signal.h`, `unistd.h`, `sys/wait.h`, `sys/socket.h`, `sys/un.h`, `secontext.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; socket option/address constants vary by kernel headers and architecture.

Test signals: unsupported ABI paths skip rather than fail.
