# File Research: sources/os/plan9/9front/sys/src/9/sgi/mem.h

SGI/MIPS memory, MMU, exception, and address-space constants shared by C and assembly. It defines page size selection, stack/Mach sizing, CP0 registers, status/cause bits, exception codes, MIPS segments, kernel/user virtual layout, PTE bits, TLB PID counts, soft-TLB sizing, and kmap layout.

Default pages are 4 KiB; optional 16 KiB pages are noted as poor. KSEG0/KSEG1 direct maps, KSEG3 kmap, `MACHADDR`, `SPBADDR`, and cache coloring macros are central to `l.s`, `mmu.c`, and `main.c`.

The PTE defaults use noncoherent write-back caching, with comments noting MIPS 24K cache behavior and errata tradeoffs.
