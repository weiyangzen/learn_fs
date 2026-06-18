# sources/test-tools/strace/tests/sendfile.c

Purpose: Standalone or shared strace regression test for sendfile offset/count decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `sendfile`, `sendfile64`, `off_t`, `loff_t`, `getsockopt`, `setsockopt`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `SKIP_MAIN_UNDEFINED`, `__NR_sendfile`. Preprocessor knobs/macros are none visible in this file. The file has 97 source lines and was read from `sources/test-tools/strace/tests/sendfile.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 7 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases; temporary opened descriptors are used to force fd/path rendering.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `assert.h`, `errno.h`, `fcntl.h`, `stdio.h`, `stdint.h`, `stdlib.h`, `unistd.h`, `sys/socket.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; feature guards must skip cleanly on kernels/libcs without the ABI; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
