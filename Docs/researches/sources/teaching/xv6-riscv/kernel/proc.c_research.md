# File Research: sources/teaching/xv6-riscv/kernel/proc.c

Implements process table, scheduling, lifecycle, sleep/wakeup, fork/exit/wait, and helpers used by filesystem/user copy paths.

Important behavior:
- Maintains global `cpus[]`, `proc[]`, `initproc`, PID allocation, and `wait_lock`.
- `proc_mapstacks()` maps guarded kernel stacks into the kernel page table.
- `allocproc()` allocates trapframe/page table and prepares initial context.
- `userinit()` creates the first process and sets cwd to `/`.
- `kfork()`, `kexit()`, and `kwait()` manage process hierarchy and resource lifetime.
- `scheduler()`, `sched()`, `yield()`, and `forkret()` implement CPU scheduling.
- `forkret()` performs deferred filesystem initialization, then execs `/init`.
- `sleep()` and `wakeup()` provide the core blocking primitive used by pipes, log, console, locks, and virtio.
- `either_copyin()` and `either_copyout()` abstract user-vs-kernel copy for filesystem code.

Filesystem relevance: process cwd, open file duplication/closure, sleep/wakeup synchronization, and user copy helpers are all core to filesystem syscall behavior.
