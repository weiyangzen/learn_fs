# File Research: sources/os/bsd/dragonflybsd/sys/sys/ptrace.h

ptrace request constants, I/O descriptor, and kernel/userland declarations.

Key responsibilities:
- Defines traditional ptrace request constants for trace-me, read/write instruction/data space, continue, kill, step, attach, detach, and I/O.
- Reserves `PT_FIRSTMACH` for machine-specific requests and includes `machine/ptrace.h`.
- Defines `struct ptrace_io_desc` for bulk I/O between parent and traced process.
- Defines `PIOD_*` operation constants.
- Declares kernel helpers for reparenting, setting PC, single-step, and `kern_ptrace()`.
- Declares userland `ptrace()`.

Important behavior:
- Historical read/write user-area requests are commented as removed/reserved.
- `PT_IO` uses `ptrace_io_desc` to read/write instruction or data space.

Dependencies:
- Includes `sys/types.h` and machine ptrace definitions.
- Kernel APIs use `struct proc` and `struct lwp`.

Notable risks:
- ptrace request numbers are ABI and debugger-facing.
- Machine-specific request range must not collide with common requests.
