# sources/test-tools/strace/tests/setresugid.c

Purpose: Standalone or shared strace regression test for credential-changing syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `ugid2int`, `print_int`, `num_matches_id`, `main`. Important syscall/test APIs and data types are `setresuid`, `setresgid`, `setreuid`, `setregid`. Preprocessor knobs/macros are none visible in this file. The file has 91 source lines and was read from `sources/test-tools/strace/tests/setresugid.c`.

Control flow: `main` and helpers (`ugid2int`, `print_int`, `num_matches_id`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 5 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `errno.h`, `stdio.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: successful self-test prints `+++ exited with 0 +++`.
