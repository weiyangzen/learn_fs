# sources/test-tools/strace/tests/signal_receive--pidns-translation.c

Purpose: Macro-variant wrapper for `signal_receive.c`. It sets `PIDNS_TRANSLATION` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`, `signal`, `kill`, `siginfo_t`, `SIG*`. Preprocessor knobs/macros are `PIDNS_TRANSLATION`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/signal_receive--pidns-translation.c`.

Control flow: At compile time this wrapper defines its knobs and includes `signal_receive.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `signal_receive.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; pid namespace translations are architecture/runtime sensitive; signal delivery and sigset layout are architecture dependent.

Test signals: test passes when actual strace output matches the printf-generated expectation.
