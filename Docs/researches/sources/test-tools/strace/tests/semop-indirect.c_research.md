# sources/test-tools/strace/tests/semop-indirect.c

Purpose: Standalone or shared strace regression test for System V semaphore decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_semop`. Important syscall/test APIs and data types are `semop`, `semtimedop`, `semget`, `semctl`, `sembuf`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`, `SKIP_MAIN_UNDEFINED`, `ipc`, `__NR_ipc`. Preprocessor knobs/macros are `XLAT_MACROS_ONLY`. The file has 39 source lines and was read from `sources/test-tools/strace/tests/semop-indirect.c`.

Control flow: `main` and helpers (`k_semop`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `semop-common.c`, `xlat/ipccalls.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail; xlat mode variants validate raw, abbreviated, and verbose representations.
