# sources/test-tools/strace/tests/sol_tipc-group_join.c

Purpose: Standalone or shared strace regression test for TIPC socket option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `set_group_req`, `get_group_req`, `main`. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are none visible in this file. The file has 167 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-group_join.c`.

Control flow: `main` and helpers (`set_group_req`, `get_group_req`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 5 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `stdio.h`, `sys/socket.h`, `linux/tipc.h`, `xmalloc.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; injection variants append expected injected-result markers; xlat mode variants validate raw, abbreviated, and verbose representations.
