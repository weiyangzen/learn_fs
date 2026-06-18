# sources/test-tools/strace/tests/sockopt-sol_socket.c

Purpose: Standalone or shared strace regression test for socket address/option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `get_sockopt`, `set_sockopt`, `print_optval`, `main`. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_MACROS_ONLY`, `INJSTR=" (INJECTED)"`, `INJSTR=""`. The file has 321 source lines and was read from `sources/test-tools/strace/tests/sockopt-sol_socket.c`.

Control flow: `main` and helpers (`get_sockopt`, `set_sockopt`, `print_optval`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 4 explicit `for` loops and 15 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It loops over many `SOL_SOCKET` options, driving both `getsockopt` and `setsockopt` with normal, short, long, zero, and faulting optval/optlen cases.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `stdio.h`, `sys/socket.h`, `sys/un.h`, `k_sockopt.h`, `xlat/sock_options.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail; injection variants append expected injected-result markers; xlat mode variants validate raw, abbreviated, and verbose representations.
