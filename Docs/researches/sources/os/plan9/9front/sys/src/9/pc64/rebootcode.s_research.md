# File Research: sources/os/plan9/9front/sys/src/9/pc64/rebootcode.s

Reboot trampoline code copied to low physical memory and executed to relocate or enter a new kernel after paging/long mode teardown.

Key behavior:
- Starts in 64-bit mode with destination, source, and byte count arguments.
- Loads a zero-length IDT and temporary GDT.
- Far-returns into a 32-bit code segment.
- In 32-bit mode, reloads data segments, disables paging, clears CR3, disables long mode in EFER, disables PAE/PGE in CR4, and sets the stack below the target entry.
- If entry is zero, parks the CPU in a halt loop.
- Copies the new kernel image with overlap-safe forward/backward `MOVSB`.
- Jumps to the destination entry point.
- Defines temporary GDT and IDT pointer records.

Notable dependencies:
- Selector and segment constants from `mem.h`.
- `main.c` copies this code to `REBOOTADDR` and jumps to it.

Research notes:
- The trampoline deliberately avoids relying on the existing high-half kernel mapping once paging is disabled.
- The copy logic handles overlapping source/destination ranges.
