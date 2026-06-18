# sources/test-tools/strace/tests/fallocate.c

Purpose: `fallocate.c` tests fallocate mode flags and offset/length argument rendering.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `errno.h`, `fcntl.h`, `stdio.h`, `linux/falloc.h`, `xlat.h`, `xlat/falloc_flags.h`. Kernel/user ABI names observed in the full file include `fallocate`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `HAVE_FALLOCATE`, `FALLOC_FL_WRITE_ZEROES`, `FALLOC_FL_KEEP_SIZE`, `FALLOC_FL_PUNCH_HOLE`, `FALLOC_FL_NO_HIDE_STALE`, `FALLOC_FL_COLLAPSE_RANGE`, `FALLOC_FL_ZERO_RANGE`, ... (13 total), `FALLOC_FL_UNSHARE_RANGE`, `FALLOC_FL_`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `errno.h`, `fcntl.h`, `stdio.h`, `linux/falloc.h`, `xlat.h`, `xlat/falloc_flags.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 68 lines, 1587 bytes, sha256 prefix `1e05c1b3b286`.
