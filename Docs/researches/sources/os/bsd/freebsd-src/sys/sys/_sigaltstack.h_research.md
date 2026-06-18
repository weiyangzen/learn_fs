# File Research: sources/os/bsd/freebsd-src/sys/sys/_sigaltstack.h

Alternate signal stack definitions.

Key elements:
- Under XSI visibility, defines `stack_t`, `SS_ONSTACK`, `SS_DISABLE`, `MINSIGSTKSZ`, and `SIGSTKSZ`.
- Defines `struct __stack_t` unconditionally for ucontext needs.
- Under BSD visibility, aliases the structure tag as `sigaltstack`.

Dependencies:
- Includes `sys/_types.h`.

Research notes:
- The structure carries stack pointer, size, and flags for signal delivery.
- Needed by `_ucontext.h` even when public typedef visibility is restricted.
