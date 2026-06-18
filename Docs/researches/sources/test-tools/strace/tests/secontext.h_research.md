# sources/test-tools/strace/tests/secontext.h

Purpose: Shared test header that provides inline helpers and macros for related strace decoder tests. It is included by companion tests rather than run directly; the code centralizes repeated helper behavior so output formatting stays consistent across the suite.

Important APIs/types/functions: Visible local functions are `get_secontext_field`, `get_secontext_field_fd`, `get_secontext_field_file`, `reset_secontext_file`, `update_secontext_field`. Important syscall/test APIs and data types are none visible in this file. Preprocessor knobs/macros are none visible in this file. The file has 105 source lines and was read from `sources/test-tools/strace/tests/secontext.h`.

Control flow: No `main` is present. Including tests call the inline helpers/macros, which branch on build-time feature macros and either call real helpers or return empty test strings.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `xmalloc.h`, `errno.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
