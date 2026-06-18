# sources/test-tools/strace/tests/set_mempolicy_home_node.c

Purpose: Standalone or shared strace regression test for NUMA memory policy decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `sys_set_mempolicy_home_node`, `main`. Important syscall/test APIs and data types are `set_mempolicy`, `set_mempolicy_home_node`, `nodemask`, `MPOL_*`, `__NR_set_mempolicy_home_node`. Preprocessor knobs/macros are `KUL_1=((unsigned long long) (kernel_ulong_t) -1ULL)`. The file has 58 source lines and was read from `sources/test-tools/strace/tests/set_mempolicy_home_node.c`.

Control flow: `main` and helpers (`sys_set_mempolicy_home_node`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `stdint.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: successful self-test prints `+++ exited with 0 +++`.
