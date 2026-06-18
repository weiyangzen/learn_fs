# File Research: sources/os/plan9/9front/sys/src/9/omap/mem.h

OMAP memory-layout and physical-address constants.

Key contents:
- Size, bit-field, alignment, page, stack, and cache-line macros.
- Kernel/user virtual layout: `KZERO`, `L1`, `CONFADDR`, `KTZERO`, `UZERO`, `UTZERO`, `USTKTOP`, and `REBOOTADDR`.
- ARM PTE public flag mappings used by generic kernel code.
- OMAP physical addresses for SCM, clock modules, DSS/DISPC, SDMA, USB TLL/UHH/OHCI/EHCI/OTG, UARTs, MMC, interrupt controller, PRM, watchdogs, timers, GPIO, L3/GPMC/SMS/DRC, and DRAM.
- `VIRTIO` and NAND/flash mapping constants.

Research notes:
- `MAXMACH` is 1 and `MACHSIZE` is one page.
- I/O space is treated as directly mapped in the kernel address plan.
