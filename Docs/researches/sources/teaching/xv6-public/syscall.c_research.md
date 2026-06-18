# File Research: sources/teaching/xv6-public/syscall.c

System call dispatcher and user argument fetch helpers.

Key behavior:
- `fetchint` and `fetchstr` validate user addresses against current process size.
- `argint`, `argptr`, and `argstr` fetch syscall arguments from the saved user stack.
- Declares all syscall implementation functions and maps syscall numbers to handlers in `syscalls[]`.
- `syscall` reads syscall number from trapframe `eax`, dispatches, and stores return value back in `eax`.
- Unknown syscalls are reported and return `-1`.

Important interactions:
- Relies on `trap.c` storing the current trapframe in `myproc()->tf`.
