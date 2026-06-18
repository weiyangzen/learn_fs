# File Research: sources/os/bsd/freebsd-src/sys/sys/_ucontext.h

User context structure definition.

Key elements:
- Defines `ucontext_t` as `struct __ucontext`.
- First fields are `uc_sigmask` and `uc_mcontext`, intentionally ordered for compatibility with `sigcontext`.
- Includes link, alternate stack, flags, and spare fields.

Dependencies:
- Requires `__sigset_t`, `mcontext_t`, and `struct __stack_t` from including context.

Research notes:
- Used by signal handling and context switching APIs.
- Field ordering is an explicit compatibility constraint.
