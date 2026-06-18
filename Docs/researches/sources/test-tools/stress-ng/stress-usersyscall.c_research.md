## sources/test-tools/stress-ng/stress-usersyscall.c

Purpose: Implements `usersyscall`, stressing Linux syscall user dispatch and SIGSYS handling.

Important APIs/types/functions: `stress_usersyscall_info`, `stress_supported`, `stress_sigsys_handler`, optional `x86_64_syscall0`, `stress_sigsys_libc_mapping`, and `stress_usersyscall`; uses `prctl(PR_SET_SYSCALL_USER_DISPATCH)`, `syscall`, `sigaction(SA_SIGINFO)`, and architecture-specific direct syscall assembly on x86_64.

Control flow: installs a SIGSYS handler that disables dispatch and copies `siginfo`. Each loop first verifies a blocked fake syscall returns ENOSYS with dispatch disabled, then enables dispatch and expects the SIGSYS path to return the syscall number. On x86_64 it optionally configures libc address bounds so libc syscalls are allowed while raw direct syscalls are trapped.

State and persistence: process-global dispatch selector and static `siginfo` are mutated; dispatch is turned off after each test. No external persistence.

Dependencies/integration: Linux prctl user dispatch support, signal mask handling, architecture helpers, `/proc/self/maps` parsing for libc.

Risks: nested syscalls inside the handler are dangerous, hence broad signal masking and minimal handler work; unsupported kernels return skip/not-implemented.

Test signals: `VERIFY_ALWAYS`; checks return values, `SYS_USER_DISPATCH`, `si_errno`, and reports nanoseconds per trapped syscall.
