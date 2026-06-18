# sources/test-tools/strace/tests/sockaddr_xlat-Xraw-y.c

Purpose: Macro-variant wrapper for `sockaddr_xlat-Xraw.c`. It sets `SKIP_IF_PROC_IS_UNAVAILABLE=skip_if_unavailable("/proc/self/fd/")`, `FD0_PATH="</dev/null>"`, `FD7_PATH="</dev/zero>"` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`. Preprocessor knobs/macros are `SKIP_IF_PROC_IS_UNAVAILABLE=skip_if_unavailable("/proc/self/fd/")`, `FD0_PATH="</dev/null>"`, `FD7_PATH="</dev/zero>"`. The file has 4 source lines and was read from `sources/test-tools/strace/tests/sockaddr_xlat-Xraw-y.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sockaddr_xlat-Xraw.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sockaddr_xlat-Xraw.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: unsupported ABI paths skip rather than fail; path-tracing/fd-decoding variants filter or annotate descriptor output; xlat mode variants validate raw, abbreviated, and verbose representations.
