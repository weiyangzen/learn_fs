# sources/test-tools/strace/tests/clone_ptrace.c

Purpose: `clone_ptrace.c` checks clone with ptrace-related tracing and quiet attach/exit modes, validating how strace reports traced children.

Important APIs/types/functions: local functions include `handler`, `child`, `main`; macros include `QUIET_ATTACH`, `QUIET_EXIT`, `do_clone`; included headers include `tests.h`, `errno.h`, `sched.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/wait.h`, `unistd.h`. Kernel/user ABI names observed in the full file include `clone`. Prominent constants include `CLONE_PTRACE`, `SPDX`, `GPL`, `QUIET_ATTACH`, `QUIET_EXIT`, `IA64`, `SIGUSR1`, `SIG_UNBLOCK`, `NULL`, ... (18 total), `WTERMSIG`, `CLD_KILLED`, `ARRSZ_PAIR`; prominent struct names include `sigaction`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `errno.h`, `sched.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/wait.h`, `unistd.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 110 lines, 2565 bytes, sha256 prefix `aef7084fda00`.
