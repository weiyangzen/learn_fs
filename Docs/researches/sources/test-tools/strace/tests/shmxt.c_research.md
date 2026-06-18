# sources/test-tools/strace/tests/shmxt.c

Purpose: Standalone or shared strace regression test for System V shared memory decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `cleanup`, `main`. Important syscall/test APIs and data types are `shmat`, `shmdt`, `shmget`, `SHM_*`. Preprocessor knobs/macros are `SHMAT="osf_shmat"`, `SHMAT="shmat"`, `SHM_EXEC=0100000`. The file has 91 source lines and was read from `sources/test-tools/strace/tests/shmxt.c`.

Control flow: `main` and helpers (`cleanup`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 4 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: a static SysV IPC id is cleaned up through an exit handler.

Dependencies: Direct dependencies are `tests.h`, `stdio.h`, `stdlib.h`, `sys/shm.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
