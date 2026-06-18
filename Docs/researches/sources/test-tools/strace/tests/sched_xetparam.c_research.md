# sources/test-tools/strace/tests/sched_xetparam.c

Purpose: Standalone or shared strace regression test for scheduler syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `sched_getattr`, `sched_setattr`, `sched_getparam`, `sched_setparam`, `sched_getscheduler`, `sched_setscheduler`, `sched_yield`, `PIDNS_TEST_INIT`, `pidns_print_leader`, `pidns_pid2str`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `__NR_sched_getparam`, `__NR_sched_setparam`. Preprocessor knobs/macros are none visible in this file. The file has 44 source lines and was read from `sources/test-tools/strace/tests/sched_xetparam.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It targets `sched_getparam`/`sched_setparam` with live pid, pid-zero, bogus pid, `struct sched_param`, invalid pointers, and optional pid namespace translation.

State and persistence behavior: tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `pidns.h`, `sched.h`, `stdio.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: pid namespace translations are architecture/runtime sensitive.

Test signals: successful self-test prints `+++ exited with 0 +++`; pid namespace runs include translated leader lines.
