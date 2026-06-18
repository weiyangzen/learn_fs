# sources/test-tools/strace/tests/scno_tampering.sh

Purpose: Shell harness for a strace self-test scenario. It runs compiled test programs through the local test-driver helpers and validates strace output behavior from the shell layer.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are none visible in this file. Preprocessor knobs/macros are none visible in this file. The file has 13 source lines and was read from `sources/test-tools/strace/tests/scno_tampering.sh`.

Control flow: The shell flow sources the test framework, chooses the compiled test program and strace options, runs the trace, then compares normalized output against expectations.

State and persistence behavior: state is limited to temporary trace/output files managed by the test framework.

Dependencies: Direct dependencies are `init.sh`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: shell comparison succeeds through the shared strace test harness.
