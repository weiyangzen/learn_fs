# sources/test-tools/strace/tests/stack-fcall.h

Purpose: Shared test header that provides inline helpers and macros for related strace decoder tests. It is included by companion tests rather than run directly; the code centralizes repeated helper behavior so output formatting stays consistent across the suite.

Important APIs/types/functions: Visible local functions are `f0`, `f1`, `f2`, `f3`. Important syscall/test APIs and data types are `backtrace`, `stack trace`, `fcall`, `mangled names`, `gettid`, `__NR_gettid`. Preprocessor knobs/macros are `f0=_ZN2ns2f0Ei`, `f1=_ZN2ns2f1Ei`, `f2=_ZN2ns2f2Ei`, `f3=_ZN2ns2f3Ei`. The file has 45 source lines and was read from `sources/test-tools/strace/tests/stack-fcall.h`.

Control flow: No `main` is present. Including tests call the inline helpers/macros, which branch on build-time feature macros and either call real helpers or return empty test strings.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `unistd.h`, `scno.h`, `gcc_compat.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
