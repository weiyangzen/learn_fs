# File Research: sources/teaching/xv6-riscv/kernel/trampoline.S

Assembly trampoline mapped at the same high virtual address in user and kernel page tables for trap entry and return.

Important behavior:
- `uservec` saves user registers into the per-process trapframe.
- Switches from user page table to kernel page table using trapframe `kernel_satp`.
- Restores kernel stack, hart ID, and jumps to `usertrap()`.
- `userret` switches to the user page table, restores user registers, restores `a0`, and executes `sret`.

Filesystem relevance: syscall entry and return use this path. Every filesystem syscall depends on this code preserving user register state and safely switching page tables.
