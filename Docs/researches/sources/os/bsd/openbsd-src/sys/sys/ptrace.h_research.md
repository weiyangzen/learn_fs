# File Research: sources/os/bsd/openbsd-src/sys/sys/ptrace.h

Defines ptrace request ABI, ptrace I/O descriptors, event/state structures, thread enumeration, and kernel MD process-debug hooks.

Key contents:
- Core requests: trace-me, read/write instruction/data, continue, kill, attach, detach, I/O.
- `struct ptrace_io_desc` and `PIOD_*` operations including auxv read.
- Event mask requests and `PTRACE_FORK`.
- Process state and thread state structures.
- Machine-dependent request inclusion via `<machine/ptrace.h>` and kernel compile check for `PT_GETREGS`/`PT_SETREGS`.

Kernel APIs:
- Process tracing helpers for reparent/untrace, read/write regs and fpregs, set PC, single-step, I/O permission check, and memory I/O.
- Userland `ptrace()` prototype.

Risk notes:
- The header enforces that machine-dependent ptrace support is complete for register get/set operations.
