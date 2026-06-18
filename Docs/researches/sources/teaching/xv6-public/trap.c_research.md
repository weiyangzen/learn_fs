# File Research: sources/teaching/xv6-public/trap.c

Interrupt/trap initialization and central trap handler.

Key behavior:
- Builds IDT entries for all 256 vectors, with syscall vector user-callable as a trap gate.
- Initializes `tickslock` and loads IDT with `lidt`.
- `trap` handles syscalls, timer, IDE, keyboard, UART, spurious interrupts, and unexpected traps.
- Timer interrupt on CPU 0 increments `ticks` and wakes sleepers.
- Unexpected kernel traps panic; unexpected user traps mark process killed.
- Killed user processes exit before/after syscalls and before returning to user mode.
- Running processes yield on timer interrupts.

Important interactions:
- Calls subsystem interrupt handlers and `lapiceoi`.
- Uses `myproc`, `yield`, and `exit` to connect traps to scheduling.
