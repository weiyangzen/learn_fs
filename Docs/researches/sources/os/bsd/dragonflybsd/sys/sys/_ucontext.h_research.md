# File Research: sources/os/bsd/dragonflybsd/sys/sys/_ucontext.h

Read completely: 81 lines.

This header defines user context and signal stack types.

Key contents:
- Includes signal-set and machine-specific machine context definitions.
- Defines `sigset_t`, `size_t`, and `stack_t` if needed.
- Defines `ucontext_t` with `uc_sigmask` and `uc_mcontext` first, then link, stack, coroutine function pointer, argument, and spare fields.

Important interactions:
- The first two fields are intentionally ordered to support compatibility with `sigcontext`/`ucontext_t` union-style handling.

Security/reliability notes:
- No runtime behavior. Layout is ABI-sensitive for signal delivery, context switching APIs, and architecture-specific `mcontext_t`.
