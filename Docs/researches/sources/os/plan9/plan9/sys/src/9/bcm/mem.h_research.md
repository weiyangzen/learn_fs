# File Research: sources/os/plan9/plan9/sys/src/9/bcm/mem.h

BCM memory layout and machine constants used by C and assembly.

Key contents:
- Page, stack, Mach, and CPU-count constants.
- Kernel virtual layout: `KZERO`, `CONFADDR`, `MACHADDR`, `L2`, `VCBUFFER`, `FIQSTKTOP`, `L1`, `KTZERO`, `VIRTIO`, and `FRAMEBUFFER`.
- User virtual layout: `UZERO`, `UTZERO`, `USTKTOP`, `USTKSIZE`, `TSTKTOP`.
- Reboot trampoline address `REBOOTADDR`.
- Cache line, PTE map, segment map, and PTE flag definitions.
- Physical/bus address constants for DRAM and I/O: `PHYSDRAM`, `BUSDRAM`, `PHYSIO`, `BUSIO`, `DRAMSIZE`, `IOSIZE`.

This file defines the fixed address contract used by boot assembly, MMU setup, DMA, framebuffer mapping, and reboot code.
