# sources/test-tools/strace/tests/seccomp-filter-v.c

Purpose: Standalone or shared strace regression test for seccomp syscall and filter decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `seccomp`, `prctl`, `SECCOMP_*`, `sock_filter`, `BPF_STMT`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `SKIP_MAIN_UNDEFINED`, `get_thread_area`, `__NR_seccomp`. Preprocessor knobs/macros are `SOCK_FILTER_KILL_PROCESS=\`. The file has 188 source lines and was read from `sources/test-tools/strace/tests/seccomp-filter-v.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 2 explicit `for` loops and 5 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It is the verbose-oriented seccomp filter test, emphasizing BPF instruction formatting and SECCOMP return/action names.

State and persistence behavior: tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `errno.h`, `stddef.h`, `stdio.h`, `unistd.h`, `sys/prctl.h`, `linux/seccomp.h`, `linux/filter.h`, `scno.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; feature guards must skip cleanly on kernels/libcs without the ABI; seccomp behavior depends on kernel support and filter side effects.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
