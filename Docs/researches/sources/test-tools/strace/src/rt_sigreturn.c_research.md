# sources/test-tools/strace/src/rt_sigreturn.c

Purpose: Decodes `rt_sigreturn` syscall context, usually by delegating to signal-frame helpers.

Important APIs/types/functions: `SYS_FUNC(rt_sigreturn)` and architecture-specific frame decode integration.

Control flow: on syscall entry/exit, obtains the tracee's signal frame context and prints restored signal mask/context where implemented; return-value handling is special because sigreturn restores user context rather than returning normally.

State and persistence: uses per-tracee register/stack state only.

Dependencies/integration: `rt_sigframe.c`, signal mask printers, architecture register hooks, and core syscall restart/return handling.

Risks: wrong frame interpretation can confuse syscall state around signal returns. Some architectures may intentionally print minimal output.

Test signals: signal delivery/return integration tests, interrupted syscalls, invalid frame pointers, and architecture build coverage.
