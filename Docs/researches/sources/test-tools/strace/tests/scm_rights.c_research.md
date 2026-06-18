# sources/test-tools/strace/tests/scm_rights.c

Purpose: Standalone or shared strace regression test for ancillary socket message decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `sendmsg`, `recvmsg`, `cmsghdr`, `SCM_CREDENTIALS`, `SCM_RIGHTS`, `SCM_PIDFD`, `msghdr`, `getsockopt`, `setsockopt`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`. Preprocessor knobs/macros are none visible in this file. The file has 86 source lines and was read from `sources/test-tools/strace/tests/scm_rights.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 2 explicit `for` loops and 2 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It sends fd rights through UNIX socket ancillary data and validates fd array printing, truncation behavior, and path-qualified descriptor output.

State and persistence behavior: temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases; temporary opened descriptors are used to force fd/path rendering.

Dependencies: Direct dependencies are `tests.h`, `assert.h`, `fcntl.h`, `stdlib.h`, `string.h`, `unistd.h`, `sys/socket.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; socket option/address constants vary by kernel headers and architecture.

Test signals: unsupported ABI paths skip rather than fail.
