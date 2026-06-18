# sources/test-tools/strace/tests/dup.c

Purpose: `dup.c` validates dup/dup2/dup3 decoder output, fd filtering, path decoding, and trace-fd qualifier behavior.

Important APIs/types/functions: local functions include `k_dup`, `main`; macros include `FD0_PATH`, `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `TRACE_FDS`, `PATH_TRACING`, `TRACE_FD_0`, `TRACE_OTHER_FDS`, `TRACE_FD_9`; included headers include `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `dup`. Prominent constants include `SPDX`, `GPL`, `FD0_PATH`, `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `TRACE_FDS`, `PATH_TRACING`, `TRACE_FD_0`, `TRACE_OTHER_FDS`, `TRACE_FD_9`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The test cases deliberately create, duplicate, and filter file descriptors so strace can prove descriptor qualifiers and decoded paths remain attached to the expected fd numbers.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `stdio.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 87 lines, 1720 bytes, sha256 prefix `a83a2d7d028a`.
