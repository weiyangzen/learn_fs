# sources/test-tools/strace/tests/seccomp-strict.c

Purpose: Standalone or shared strace regression test for seccomp syscall and filter decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `seccomp`, `prctl`, `SECCOMP_*`, `sock_filter`, `BPF_STMT`, `exit`, `__NR_seccomp`, `__NR_exit`. Preprocessor knobs/macros are none visible in this file. The file has 47 source lines and was read from `sources/test-tools/strace/tests/seccomp-strict.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 1 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: seccomp behavior depends on kernel support and filter side effects.

Test signals: successful self-test prints `+++ exited with 0 +++`.
