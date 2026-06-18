# sources/test-tools/strace/tests/stat.c

Purpose: Standalone or shared strace regression test for stat/statfs/statmount decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `stat`, `stat64`, `statfs`, `statfs64`, `statmount`, `SKIP_MAIN_UNDEFINED`. Preprocessor knobs/macros are `TEST_SYSCALL_NR=__NR_stat`, `TEST_SYSCALL_STR="stat"`, `SAMPLE_SIZE=((libc_off_t) (kernel_ulong_t) 43147718418ULL)`. The file has 23 source lines and was read from `sources/test-tools/strace/tests/stat.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `lstatx.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
