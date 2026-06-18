# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___sigaction14_sigtramp.c

Read completely: 82 lines.

This implements `__libc_sigaction14`, weak-aliased as `__sigaction14`. It calls `__sigaction_sigtramp`, choosing no trampoline when `act == NULL`, a legacy sigcontext trampoline when available and `SA_SIGINFO` is not set, otherwise the siginfo trampoline.

Important interactions: preserves historical signal trampoline selection while using the modern trampoline registration backend.

Security/reliability notes: it preserves `errno` when the sigcontext trampoline probe fails with `EINVAL` and retries with siginfo. This is delicate ABI logic around signal delivery.
