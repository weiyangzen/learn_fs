# File Research: sources/teaching/xv6-riscv/kernel/trap.c

Implements user/kernel trap handling, timer ticks, syscall dispatch entry, page fault handling, and device interrupt routing.

Important behavior:
- `trapinit()` initializes tick lock.
- `trapinithart()` installs `kernelvec`.
- `usertrap()` handles syscalls, device interrupts, lazy page faults, unexpected traps, kill checks, and timer yields.
- `prepare_return()` configures trampoline return state and user trap vector.
- `kerneltrap()` handles kernel-mode device interrupts and panics on unexpected traps.
- `clockintr()` increments ticks and schedules next timer interrupt.
- `devintr()` claims PLIC interrupts, dispatches UART or virtio disk interrupts, completes PLIC claims, and handles timer interrupts.

Filesystem relevance: virtio disk completion interrupts wake block I/O. Syscalls enter through `usertrap()`. Lazy page faults can allocate user buffers touched by read/write paths.
