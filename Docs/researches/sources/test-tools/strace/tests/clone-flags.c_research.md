# sources/test-tools/strace/tests/clone-flags.c

Purpose: `clone-flags.c` prints and validates clone flag xlat combinations, signal bits, and unknown-bit handling used by clone-family decoders.

Important APIs/types/functions: local functions include `retrieve_userns`, `wait_cloned`, `child`, `main`; macros include `do_clone`, `do_clone_newns`, `SYSCALL_NAME`, `STACK_SIZE_FMT`, `STACK_SIZE_ARG`; included headers include `tests.h`, `xmalloc.h`, `errno.h`, `limits.h`, `sched.h`, `signal.h`, `stdio.h`, ... (11 total), `sys/wait.h`, `unistd.h`, `linux/sched.h`. Kernel/user ABI names observed in the full file include `clone`. Prominent constants include `SPDX`, `GPL`, `WIFEXITED`, `WEXITSTATUS`, `IA64`, `NULL`, `SYSCALL_NAME`, `STACK_SIZE_FMT`, `STACK_SIZE_ARG`, ... (18 total), `PATH_MAX`, `CLONE_PIDFD`, `CLONE_NEWUSER`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `xmalloc.h`, `errno.h`, `limits.h`, `sched.h`, `signal.h`, `stdio.h`, ... (11 total), `sys/wait.h`, `unistd.h`, `linux/sched.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 192 lines, 6189 bytes, sha256 prefix `f137b9f7a803`.
