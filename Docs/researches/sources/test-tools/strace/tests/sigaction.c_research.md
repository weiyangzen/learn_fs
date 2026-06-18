# sources/test-tools/strace/tests/sigaction.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_sigaction`, `main`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `SKIP_MAIN_UNDEFINED`, `__NR_sigaction`. Preprocessor knobs/macros are `ADDR_INT=((unsigned int) -0xdefaced)`, `SIGNO_INT=((unsigned int) -SIGUSR1)`, `SIG_STR="-SIGUSR1"`, `ADDR_INT=((unsigned int) 0xdefaced)`, `SIGNO_INT=((unsigned int) SIGUSR1)`, `SIG_STR="SIGUSR1"`, `SA_RESTORER_FMT=", sa_flags=SA_RESTORER, sa_restorer=%#lx"`, `SA_RESTORER_ARGS=, new_act->restorer`, `SA_RESTORER_FMT=", sa_flags=SA_NODEFER"`, `SA_RESTORER_ARGS`. The file has 186 source lines and was read from `sources/test-tools/strace/tests/sigaction.c`.

Control flow: `main` and helpers (`k_sigaction`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 1 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `signal.h`, `stdint.h`, `stdio.h`, `string.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; feature guards must skip cleanly on kernels/libcs without the ABI; signal delivery and sigset layout are architecture dependent.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
