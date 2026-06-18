# sources/test-tools/strace/tests/close_range.c

Purpose: `close_range.c` tests filesystem utility syscall decoding for file creation, temp-file creation, range copy, close_range, sockets/helpers, and synchronization wrappers.

Important APIs/types/functions: local functions include `k_close_range`, `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `linux/close_range.h`. Kernel/user ABI names observed in the full file include `close_range`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `CLOSE_RANGE_`, `CLOSE_RANGE_UNSHARE`, `CLOSE_RANGE_CLOEXEC`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `linux/close_range.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 79 lines, 2091 bytes, sha256 prefix `572bde4ef7cf`.
