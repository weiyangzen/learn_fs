# sources/test-tools/strace/src/linux/ia64/rt_sigframe.h

Purpose: defines the `ia64` realtime signal-frame layout used by strace.

Important APIs/types/functions: STRACE_RT_SIGFRAME_H, OFFSETOF_SIGMASK_IN_RT_SIGFRAME; struct typedef count 1.

Control flow: no direct runtime flow in the header; generic frame decoders use the typedef and offset macros when reading tracee memory.

State/persistence behavior: reads transient signal-frame data from tracee memory and prints it; no durable state is stored.

Dependencies/integration: integrates with `get_stack_pointer`, `umove_or_printaddr`, sigset printers, `ucontext_t`/`sigcontext`, and generic signal-return decoding.

Risks/test signals: frame offsets and padding are ABI-sensitive; validate with signal handler traces, blocked-mask restoration, and rt_sigreturn decoding on the architecture.

Source-read signal: reviewed complete local file (25 lines).
