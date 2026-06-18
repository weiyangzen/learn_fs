# File Research: sources/teaching/xv6-public/usys.S

User-space syscall stub generator.

Behavior:
- Defines `SYSCALL(name)` macro that emits a global function, loads `SYS_name` into `%eax`, executes `int T_SYSCALL`, and returns.
- Emits stubs for all xv6 system calls.

Role:
- Bridges C user programs to the kernel syscall trap ABI.
