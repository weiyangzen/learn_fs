# File Research: sources/teaching/xv6-riscv/kernel/start.c

Machine-mode startup code called from `entry.S`.

Important behavior:
- Allocates `stack0`, one boot stack per CPU.
- Sets machine previous privilege to supervisor and `mepc` to `main`.
- Disables paging initially.
- Delegates interrupts/exceptions to supervisor mode.
- Enables supervisor external and timer interrupts.
- Configures PMP to allow supervisor access to physical memory.
- Initializes timer interrupt support and stores hart ID in `tp`.
- Enters supervisor mode with `mret`.

Filesystem relevance: indirect. It establishes privilege, timer interrupts, and CPU identity needed before the kernel can initialize storage and filesystem subsystems.
