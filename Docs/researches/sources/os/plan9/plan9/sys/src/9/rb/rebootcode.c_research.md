# File Research: sources/os/plan9/plan9/sys/src/9/rb/rebootcode.c

Small MIPS reboot trampoline copied to `REBOOTADDR` by `reboot()` before jumping into a newly loaded kernel.

Key responsibilities:
- Prints `Boot` through the raw i8250-compatible console registers.
- Saves incoming entry/code/size arguments in static variables before moving the stack near the new kernel entry.
- Copies the loaded kernel image from `code` to `entry`, cleans caches, enforces coherence, and jumps to the new entry point.
- Provides local `putc` polling on the UART line-status register.
- Supplies stub `syscall` and `trap` definitions so the tiny trampoline can link.

Dependencies and assumptions:
- Runs in KSEG0/direct-mapped space with TLBs ignored.
- Assumes the serial console is at `PHYSCONS` and register spacing matches the port's 32-bit CSR access style.
- Assumes `setsp`, `memmove`, `cleancache`, and `coherence` are safe in the reboot context.

Notable risks:
- The stack is deliberately moved to `entry - 0x20 - 4`; overlap with the target image layout would be fatal.
- If the new kernel returns, the code only prints `?!` and loops forever.
