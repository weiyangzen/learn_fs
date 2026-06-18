# File Research: sources/os/bsd/freebsd-src/sys/sys/_stack.h

Kernel stack trace storage definition.

Key elements:
- Defines `STACK_MAX` as 18.
- Defines `struct stack` with depth and an array of program counters.

Dependencies:
- Requires `vm_offset_t` from including context.

Research notes:
- Used by debug/profiling facilities, including optional lock debugging in `_lockmgr.h`.
