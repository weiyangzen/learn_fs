# sources/test-tools/strace/tests/sched_xetattr.c

Purpose: Standalone or shared strace regression test for scheduler syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `sys_sched_getattr`, `sys_sched_setattr`, `main`. Important syscall/test APIs and data types are `sched_getattr`, `sched_setattr`, `sched_getparam`, `sched_setparam`, `sched_getscheduler`, `sched_setscheduler`, `sched_yield`, `PIDNS_TEST_INIT`, `pidns_print_leader`, `pidns_pid2str`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`, plus 2 more. Preprocessor knobs/macros are none visible in this file. The file has 463 source lines and was read from `sources/test-tools/strace/tests/sched_xetattr.c`.

Control flow: `main` and helpers (`sys_sched_getattr`, `sys_sched_setattr`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 13 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It exercises both `sched_getattr` and `sched_setattr`, including null pointers, bogus pids, oversized and undersized `struct sched_attr`, util-clamp fields, flag decoding, f8-filled high bits, and pid namespace print leaders.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `sched.h`, `unistd.h`, `linux/sched/types.h`, `pidns.h`, `xlat.h`, `xlat/schedulers.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: pid namespace translations are architecture/runtime sensitive; fault-address tests depend on tail allocation and pointer-width behavior.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail; pid namespace runs include translated leader lines.
