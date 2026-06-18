# sources/test-tools/strace/tests/epoll_ctl.c

Purpose: `epoll_ctl.c` covers epoll creation, control, wait, pwait, and pwait2 decoders, including event masks, timeout structures, sigmask pointers, and fd/path variants.

Important APIs/types/functions: local functions include `invoke_syscall`, `main`; macros include none detected; included headers include `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `unistd.h`, `linux/eventpoll.h`. Kernel/user ABI names observed in the full file include `epoll_ctl`. Prominent constants include `SPDX`, `GPL`, `F8ILL_KULONG_MASK`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `EPOLLIN`, `EPOLL_CTL_ADD`, `EPOLL_CTL_DEL`, `EPOLL_CTL_MOD`, `NULL`; prominent struct names include `epoll_event`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The epoll tests create descriptors/events, drive control or wait calls, and print event masks, timeout values, and signal-mask arguments in the same shape strace should decode.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `unistd.h`, `linux/eventpoll.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 46 lines, 1096 bytes, sha256 prefix `a0aa16644aa5`.
