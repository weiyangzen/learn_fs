# sources/test-tools/strace/tests/setrlimit.c

Purpose: Standalone or shared strace regression test for resource limit decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `setrlimit`, `rlimit`, `RLIMIT_*`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`, `SKIP_MAIN_UNDEFINED`, `__NR_setrlimit`. Preprocessor knobs/macros are none visible in this file. The file has 77 source lines and was read from `sources/test-tools/strace/tests/setrlimit.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 2 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `xgetrlimit.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior; feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail; xlat mode variants validate raw, abbreviated, and verbose representations.
