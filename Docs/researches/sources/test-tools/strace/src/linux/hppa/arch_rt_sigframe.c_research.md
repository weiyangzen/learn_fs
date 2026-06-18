# sources/test-tools/strace/src/linux/hppa/arch_rt_sigframe.c

Purpose: computes the address of the `hppa` realtime signal frame.

Important APIs/types/functions: SIGFRAME; struct typedef count 0.

Control flow: obtains the tracee stack pointer and applies the architecture's frame offset adjustment before returning the address to generic signal-frame decoders.

State/persistence behavior: reads transient signal-frame data from tracee memory and prints it; no durable state is stored.

Dependencies/integration: integrates with `get_stack_pointer`, `umove_or_printaddr`, sigset printers, `ucontext_t`/`sigcontext`, and generic signal-return decoding.

Risks/test signals: frame offsets and padding are ABI-sensitive; validate with signal handler traces, blocked-mask restoration, and rt_sigreturn decoding on the architecture.

Source-read signal: reviewed complete local file (45 lines).
