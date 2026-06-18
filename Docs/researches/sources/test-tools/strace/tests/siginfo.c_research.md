# sources/test-tools/strace/tests/siginfo.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `handler`, `main`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`. Preprocessor knobs/macros are none visible in this file. The file has 177 source lines and was read from `sources/test-tools/strace/tests/siginfo.c`.

Control flow: `main` and helpers (`handler`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 9 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: child process state is synchronized with wait/signal helpers.

Dependencies: Direct dependencies are `tests.h`, `assert.h`, `signal.h`, `string.h`, `unistd.h`, `sys/wait.h`, `time_enjoyment.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: signal delivery and sigset layout are architecture dependent.

Test signals: successful self-test prints `+++ exited with 0 +++`.
