# sources/test-tools/strace/tests/sigreturn.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `handler`, `main`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`, `SKIP_MAIN_UNDEFINED`, `sigreturn`. Preprocessor knobs/macros are `RT_0=ASM_SIGRTMIN`, `RT_0=32`. The file has 73 source lines and was read from `sources/test-tools/strace/tests/sigreturn.c`.

Control flow: `main` and helpers (`handler`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 3 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `signal.h`, `stdio.h`, `stdlib.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI; signal delivery and sigset layout are architecture dependent.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
