# File Research: sources/os/plan9/9front/sys/src/9/mtx/io.h

This header defines MTX interrupt numbers, vector ranges, `Vctl`, EISA constants, PCI DMA address mapping, and `BUSUNKNOWN`.

`Vctl` is the per-interrupt handler record used by the trap/interrupt code. It stores next-handler chain, driver name, IRQ, TBDF, optional ISR/EOI callbacks, function pointer, and argument.

`PCIWADDR(va)` maps a kernel virtual address to a PCI-window bus address via `PADDR(va)+PCIWINDOW`, which is used by the Ethernet driver’s DMA descriptors.

Filesystem relevance is mainly device/driver infrastructure: interrupt dispatch and DMA address translation affect block, serial, and network device files.

Notable risks: `PCIWADDR` assumes the Raven PCI window configuration from `raven.c`.
