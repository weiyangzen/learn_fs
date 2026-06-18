# sources/test-tools/strace/tests/check_sigign.c

Purpose: `check_sigign.c` is a strace regression test source for one syscall decoder or helper surface in the test suite.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `signal.h`, `stdlib.h`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `SIG_IGN`, `SIG_DFL`, `SPDX`, `GPL`, `NULL`; prominent struct names include `sigaction`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `signal.h`, `stdlib.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 29 lines, 616 bytes, sha256 prefix `0665e3de3dc6`.
