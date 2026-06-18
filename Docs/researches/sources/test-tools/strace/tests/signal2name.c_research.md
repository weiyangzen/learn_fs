# sources/test-tools/strace/tests/signal2name.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `signal2name`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`, `signal`, `kill`, `siginfo_t`, `SIG*`. Preprocessor knobs/macros are none visible in this file. The file has 63 source lines and was read from `sources/test-tools/strace/tests/signal2name.c`.

Control flow: `main` and helpers (`signal2name`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `signal.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; signal delivery and sigset layout are architecture dependent.

Test signals: test passes when actual strace output matches the printf-generated expectation.
