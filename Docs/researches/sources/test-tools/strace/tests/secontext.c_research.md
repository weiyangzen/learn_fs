# sources/test-tools/strace/tests/secontext.c

Purpose: Standalone or shared strace regression test for a Linux syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `secontext_format`, `strip_trailing_newlines`, `get_secontext_field`, `raw_expected_secontext_full_file`, `raw_expected_secontext_short_file`, `raw_secontext_full_file`, `raw_secontext_full_fd`, `get_secontext_field_file`, `get_secontext_field_fd`, `raw_secontext_short_file`, `raw_secontext_short_fd`, `raw_secontext_full_pid`, plus 9 more. Important syscall/test APIs and data types are none visible in this file. Preprocessor knobs/macros are `TEST_SECONTEXT`. The file has 338 source lines and was read from `sources/test-tools/strace/tests/secontext.c`.

Control flow: `main` and helpers (`secontext_format`, `strip_trailing_newlines`, `get_secontext_field`, `raw_expected_secontext_full_file`, `raw_expected_secontext_short_file`, `raw_secontext_full_file`, `raw_secontext_full_fd`, `get_secontext_field_file`, `get_secontext_field_fd`, `raw_secontext_short_file`, plus 11 more) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 3 explicit `for` loops and 19 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It implements the SELinux/security-context helper test body, including formatting wrappers for fd, file, process, and missing-context cases.

State and persistence behavior: temporary opened descriptors are used to force fd/path rendering.

Dependencies: Direct dependencies are `tests.h`, `assert.h`, `errno.h`, `stdlib.h`, `string.h`, `sys/stat.h`, `unistd.h`, `selinux/selinux.h`, `selinux/label.h`, `xmalloc.h`, `secontext.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
