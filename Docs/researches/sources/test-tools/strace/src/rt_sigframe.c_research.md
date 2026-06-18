# sources/test-tools/strace/src/rt_sigframe.c

Purpose: Architecture hook for decoding real-time signal frames when a traced task is in signal-return context.

Important APIs/types/functions: signal-frame decoder entry points used by `rt_sigreturn.c`.

Control flow: fetches architecture-specific frame data from the tracee stack/register state and prints or makes available saved signal context fields.

State and persistence: reads per-tracee register/stack state; no global persistence.

Dependencies/integration: architecture signal frame layouts, `rt_sigreturn` decoder, ptrace register access, and sigset/siginfo printers.

Risks: signal-frame layout is highly architecture and libc/kernel dependent; invalid stack pointers must fail gracefully.

Test signals: rt_sigreturn tests on supported architectures, invalid/restored stack frames, and signal mask/context output.
