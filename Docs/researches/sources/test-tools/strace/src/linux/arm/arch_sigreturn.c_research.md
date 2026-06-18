# sources/test-tools/strace/src/linux/arm/arch_sigreturn.c

Purpose: decodes signal mask restoration for `arm` `sigreturn`/`rt_sigreturn` handling.

Important APIs/types/functions: arch_sigreturn, SIZEOF_STRUCT_SIGINFO, SIZEOF_STRUCT_SIGCONTEXT, OFFSETOF_STRUCT_UCONTEXT_UC_SIGMASK; struct typedef count 0.

Control flow: the helper locates the signal frame from the current stack pointer or architecture context, reads the relevant frame/mask fields with safe `umove` helpers, and prints the restored signal mask.

State/persistence behavior: reads transient signal-frame data from tracee memory and prints it; no durable state is stored.

Dependencies/integration: integrates with `get_stack_pointer`, `umove_or_printaddr`, sigset printers, `ucontext_t`/`sigcontext`, and generic signal-return decoding.

Risks/test signals: frame offsets and padding are ABI-sensitive; validate with signal handler traces, blocked-mask restoration, and rt_sigreturn decoding on the architecture.

Source-read signal: reviewed complete local file (28 lines).
