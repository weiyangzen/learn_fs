# File Research: sources/os/plan9/9front/sys/src/9/bcm64/fns.h

ARM64 BCM function declarations and architecture helper macros.

Key contents:
- Declares low-level assembly helpers for events, atomics, barriers, interrupt priority, user return, labels, FP register save/restore, TLB/cache maintenance, MMU setup, and physical/virtual mapping.
- Declares clock, FP, trap, interrupt, GPIO, UART, DMA, mailbox, framebuffer, PCI, and reboot/platform helpers.
- Defines `PADDR`, `KADDR`, `VA`, `cycles()`, and `getpgcolor()`.

Role:
- Central prototype header joining ARM64 assembly, platform drivers, and Plan 9 port code.

Dependencies:
- `dat.h`, `mem.h`, and all architecture subsystems.
