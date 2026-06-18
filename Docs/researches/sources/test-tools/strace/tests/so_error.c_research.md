# sources/test-tools/strace/tests/so_error.c

Purpose: Standalone or shared strace regression test for SOL_SOCKET option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `reserve_ephemeral_port`, `main`. Important syscall/test APIs and data types are `getsockopt`, `setsockopt`, `SO_*`, `SOL_SOCKET`, `socklen_t`, `connect`, `sockaddr decoding`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`. Preprocessor knobs/macros are none visible in this file. The file has 134 source lines and was read from `sources/test-tools/strace/tests/so_error.c`.

Control flow: `main` and helpers (`reserve_ephemeral_port`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 2 explicit `for` loops and 14 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `errno.h`, `fcntl.h`, `netinet/in.h`, `stdio.h`, `sys/select.h`, `sys/socket.h`, `sys/types.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
