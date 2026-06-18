# sources/test-tools/strace/tests/cachestat.c

Purpose: `cachestat.c` covers the cachestat syscall decoder, its range/stat structures, fd/path qualification variants, and success/error output formatting.

Important APIs/types/functions: local functions include `k_cachestat`, `main`; macros include `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD9_PATH`, `INJ_STR`, `TRACE_FDS`, `TRACE_PATH`, `TRACE_FILTERED`; included headers include `tests.h`, `scno.h`, `cachestat.h`, `stdio.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `cachestat`. Prominent constants include `SPDX`, `GPL`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD9_PATH`, `RETVAL_INJECTED`, `INJ_STR`, `INJECTED`, `TRACE_FDS`, `TRACE_PATH`, `TRACE_FILTERED`, `NULL`, `TAIL_ALLOC_OBJECT_CONST_PTR`; prominent struct names include `cachestat_range`, `cachestat`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `cachestat.h`, `stdio.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 108 lines, 2886 bytes, sha256 prefix `56d39a48c47e`.
