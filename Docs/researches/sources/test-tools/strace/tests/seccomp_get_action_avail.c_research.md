# sources/test-tools/strace/tests/seccomp_get_action_avail.c

Purpose: Standalone or shared strace regression test for seccomp syscall and filter decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_seccomp`, `main`. Important syscall/test APIs and data types are `seccomp`, `prctl`, `SECCOMP_*`, `sock_filter`, `BPF_STMT`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `__NR_seccomp`. Preprocessor knobs/macros are none visible in this file. The file has 77 source lines and was read from `sources/test-tools/strace/tests/seccomp_get_action_avail.c`.

Control flow: `main` and helpers (`k_seccomp`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 1 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `stdio.h`, `stdint.h`, `unistd.h`, `linux/seccomp.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; seccomp behavior depends on kernel support and filter side effects.

Test signals: successful self-test prints `+++ exited with 0 +++`.
