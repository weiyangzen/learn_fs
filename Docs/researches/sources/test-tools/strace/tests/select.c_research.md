# sources/test-tools/strace/tests/select.c

Purpose: Standalone or shared strace regression test for select fd-set/path-tracing decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `select`, `fd_set`, `FD_SET`, `timeval`, `SKIP_MAIN_UNDEFINED`, `_newselect`. Preprocessor knobs/macros are `TEST_SYSCALL_NR=__NR_select`, `TEST_SYSCALL_STR="select"`. The file has 22 source lines and was read from `sources/test-tools/strace/tests/select.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `xselect.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
