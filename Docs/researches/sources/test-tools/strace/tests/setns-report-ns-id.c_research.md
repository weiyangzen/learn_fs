# sources/test-tools/strace/tests/setns-report-ns-id.c

Purpose: Standalone or shared strace regression test for namespace switching decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `setns`, `open`, `/proc/self/ns`, `CLONE_NEW*`, `unshare`, `__NR_unshare`, `__NR_setns`. Preprocessor knobs/macros are none visible in this file. The file has 49 source lines and was read from `sources/test-tools/strace/tests/setns-report-ns-id.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 5 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: temporary opened descriptors are used to force fd/path rendering.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `limits.h`, `stdio.h`, `unistd.h`, `fcntl.h`, `errno.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
