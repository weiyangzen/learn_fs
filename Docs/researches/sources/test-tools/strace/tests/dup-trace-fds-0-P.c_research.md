# sources/test-tools/strace/tests/dup-trace-fds-0-P.c

Purpose: `dup-trace-fds-0-P.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include none detected; macros include `TRACE_FDS`, `TRACE_FD_0`; included headers include `dup-P.c`. Kernel/user ABI names observed in the full file include `dup`. Prominent constants include `TRACE_FDS`, `TRACE_FD_0`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.  This is a wrapper/variant file that reuses shared test implementation through local includes: `dup-P.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `dup-P.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 3 lines, 65 bytes, sha256 prefix `94f523ce5b5b`.
