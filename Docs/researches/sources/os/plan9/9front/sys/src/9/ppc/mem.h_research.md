# File Research: sources/os/plan9/9front/sys/src/9/ppc/mem.h

PowerPC memory, register, exception, PTE, and address-space constants.

Key responsibilities:
- Includes either `ucu.h` or `blast.h` depending on `ucuconf`.
- Defines byte/page/cache sizes, page table entry sizes, machine/kernel stack sizes, tick constants, PPC SPR numbers, BAT register macros, 603e/604e/MPC8260 registers, and bit-numbering helpers.
- Defines MSR/SRR1 bits, exception codes, register assignments for `m` and `up`, virtual MMU constants, PTE encoding macros, HID0 bits, and address-space layout.
- Defines internal memory/I/O base addresses and page coloring.

Dependencies:
- Used by both C and assembly; its constants must match low-level PPC hardware and `l.s`.
