# sources/test-tools/strace/tests/sched_xetscheduler.c

Purpose: Standalone or shared strace regression test for scheduler syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `scheduler_str`, `main`. Important syscall/test APIs and data types are `sched_getattr`, `sched_setattr`, `sched_getparam`, `sched_setparam`, `sched_getscheduler`, `sched_setscheduler`, `sched_yield`, `PIDNS_TEST_INIT`, `pidns_print_leader`, `pidns_pid2str`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`, plus 2 more. Preprocessor knobs/macros are `XLAT_MACROS_ONLY`. The file has 123 source lines and was read from `sources/test-tools/strace/tests/sched_xetscheduler.c`.

Control flow: `main` and helpers (`scheduler_str`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It covers `sched_getscheduler` and `sched_setscheduler`, policy xlat modes, reset-on-fork flag handling, pid rendering, and errno/result formatting.

State and persistence behavior: tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `pidns.h`, `sched.h`, `stdio.h`, `unistd.h`, `xlat/schedulers.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: pid namespace translations are architecture/runtime sensitive; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior.

Test signals: successful self-test prints `+++ exited with 0 +++`; pid namespace runs include translated leader lines; xlat mode variants validate raw, abbreviated, and verbose representations.
