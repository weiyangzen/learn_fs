# File Research: sources/teaching/xv6-public/initcode.S

Tiny initial user program embedded in the kernel.

Behavior:
- Builds arguments for `exec("/init", argv)` on its initial user stack.
- Issues `SYS_exec` via `int T_SYSCALL`.
- If exec fails, loops issuing `SYS_exit`.

Important interactions:
- Linked as binary `initcode` and embedded into the kernel.
- Loaded by `userinit` at virtual address 0.
