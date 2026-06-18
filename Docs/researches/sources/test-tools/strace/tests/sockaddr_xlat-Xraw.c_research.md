# sources/test-tools/strace/tests/sockaddr_xlat-Xraw.c

Purpose: Macro-variant wrapper for `sockaddr_xlat.c`. It sets `XLAT_RAW=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_RAW=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sockaddr_xlat-Xraw.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sockaddr_xlat.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sockaddr_xlat.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
