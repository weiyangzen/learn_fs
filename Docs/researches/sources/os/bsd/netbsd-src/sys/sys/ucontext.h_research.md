# File Research: sources/os/bsd/netbsd-src/sys/sys/ucontext.h

Read completely: 115 lines.

Defines machine/user context ABI.

Key elements:
- Defines `uc_flags` bits for valid signal mask, stack, CPU context, FPU context, and reserved machine-dependent bits.
- Requires machine definitions for common MD flags `_UC_TLSBASE`, `_UC_SETSTACK`, and `_UC_CLRSTACK`.
- Includes machine `mcontext.h`.
- Defines `ucontext_t` as `struct __ucontext`.
- `struct __ucontext` contains flags, link, signal mask, stack, machine context, and optional machine padding.
- Kernel prototypes cover get/set user context, machine context get/set, and validation.
- Kernel compile-time assertion checks expected context size when defined.

Risks and notes:
- Machine context layout and flags are architecture ABI.
- Signal, TLS, and stack restoration depend on correct MD flag handling.
