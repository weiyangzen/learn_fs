# sources/test-tools/strace/tests/sleep-timing.c

Purpose: Standalone or shared strace regression test for sleep/timing trace test. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `timespec_sub`, `timespec_to_sec`, `write_timing_file`, `main`. Important syscall/test APIs and data types are `sleep`, `nanosleep`, `time`, `SKIP_MAIN_UNDEFINED`, `__NR_nanosleep`. Preprocessor knobs/macros are none visible in this file. The file has 106 source lines and was read from `sources/test-tools/strace/tests/sleep-timing.c`.

Control flow: `main` and helpers (`timespec_sub`, `timespec_to_sec`, `write_timing_file`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 11 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: temporary opened descriptors are used to force fd/path rendering.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `stdio.h`, `stdlib.h`, `time.h`, `unistd.h`, `kernel_old_timespec.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
