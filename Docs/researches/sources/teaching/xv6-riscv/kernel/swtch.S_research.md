# File Research: sources/teaching/xv6-riscv/kernel/swtch.S

Implements low-level context switching.

Important behavior:
- `swtch(old, new)` saves `ra`, `sp`, and all callee-saved registers into `old`.
- Loads the same registers from `new`.
- Returns into the newly restored context.

Filesystem relevance: indirect but foundational. Filesystem operations can sleep on locks, log space, pipes, console input, and disk I/O; sleeping depends on scheduler context switches through this routine.
