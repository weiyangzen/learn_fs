# sources/test-tools/strace/tests/setgroups.c

Purpose: Standalone or shared strace regression test for supplementary group syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `printuid`, `main`. Important syscall/test APIs and data types are `setgroups`, `gid_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `setgroups32`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setgroups32`, `SYSCALL_NAME="setgroups32"`, `GID_TYPE=unsigned int`, `SYSCALL_NR=__NR_setgroups`, `SYSCALL_NAME="setgroups"`, `GID_TYPE=unsigned short`. The file has 157 source lines and was read from `sources/test-tools/strace/tests/setgroups.c`.

Control flow: `main` and helpers (`printuid`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 2 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; credential tests must avoid assuming privilege changes succeed.

Test signals: successful self-test prints `+++ exited with 0 +++`.
