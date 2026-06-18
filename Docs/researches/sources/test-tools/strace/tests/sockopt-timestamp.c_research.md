# sources/test-tools/strace/tests/sockopt-timestamp.c

Purpose: Standalone or shared strace regression test for socket address/option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_recvmsg`, `print_timestamp_old`, `print_timestampns_old`, `print_timestamp_new`, `print_timestampns_new`, `test_sockopt`, `main`. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `sendmsg`, `recvmsg`, `msghdr`, `socklen_t`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`, `SKIP_MAIN_UNDEFINED`, `__NR_recvmsg`. Preprocessor knobs/macros are `XLAT_MACROS_ONLY`. The file has 234 source lines and was read from `sources/test-tools/strace/tests/sockopt-timestamp.c`.

Control flow: `main` and helpers (`k_recvmsg`, `print_timestamp_old`, `print_timestampns_old`, `print_timestamp_new`, `print_timestampns_new`, `test_sockopt`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 2 explicit `for` loops and 15 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It constructs timestamp control messages and socket option combinations for old/new timeval/timespec layouts and recvmsg ancillary-data decoding.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; temporary sockets/fds exist only for the test process.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `errno.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/socket.h`, `kernel_time_types.h`, `kernel_timeval.h`, `kernel_old_timespec.h`, `k_sockopt.h`, `xlat/sock_options.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; feature guards must skip cleanly on kernels/libcs without the ABI; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail; xlat mode variants validate raw, abbreviated, and verbose representations.
