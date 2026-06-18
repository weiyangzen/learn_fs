# File Research: sources/os/plan9/plan9/sys/src/9/mtx/mem.h

Defines MTX PowerPC memory layout, page/MMU constants, processor registers, trap codes, and device address windows.

Key points:
- Sets fundamental sizes: 4KB pages, 32-bit words, 8-byte `vlong`, 16-byte cache line, 4KB kernel stack, `MAXMACH` 1.
- Defines PowerPC SPR numbers for DSISR, DAR, DEC, SDR1, SRR0/1, SPRG registers, timebase, PVR, BATs, HID0/1, and 604e performance registers.
- Uses `BIT(i)` for PowerPC’s high-bit-first register numbering.
- Defines MSR bits including external interrupts, privilege, FP, machine check, instruction/data MMU, recoverable interrupt, and endian flags.
- Enumerates PowerPC exception vector codes such as reset, machine check, DSI/ISI, external interrupt, alignment, program, FP unavailable, decrementer, syscall, trace, and 604e-specific vectors.
- Reserves registers `R30` for `m` and `R29` for `up`.
- Defines hash-PTE formats (`PTE0`, WIMG/PP bits in `PTE1_*`) and Plan 9 fault-layer aliases (`PTEWRITE`, `PTERONLY`, `PTEUNCACHED`).
- Defines user/kernel virtual layout: `KZERO=0x80000000`, `KTZERO`, `UTZERO`, `USTKTOP`, user stack size, and register save size.
- Defines MTX physical/device windows: PCI memory ranges, I/O space, Falcon, Raven, flash ranges, and `isphys()`.

Dependencies and interactions:
- Included by C and assembly files.
- `mmu.c` uses PTE and VSID-related constants.
- `raven.c` and `pci.c` rely on PCI/I/O window definitions.
- Trap and syscall code uses exception and MSR constants.

Research relevance:
- This header is the architectural contract for the MTX port’s address map, trap vectors, and MMU encoding.
