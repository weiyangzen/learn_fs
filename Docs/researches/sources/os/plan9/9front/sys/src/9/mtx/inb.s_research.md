# File Research: sources/os/plan9/9front/sys/src/9/mtx/inb.s

This PowerPC assembly file implements x86-style I/O port accessors over the MTX memory-mapped I/O window at `IOMEM`. It provides byte, short, and long input/output operations plus string/block variants: `inb`, `insb`, `outb`, `outsb`, `ins`, `inss`, `outs`, `outss`, `inl`, `insl`, `outl`, and `outsl`.

The routines OR the port number with `IOMEM`, use `EIEIO` barriers around device accesses, and use byte-reversed load/store instructions for 16/32-bit scalar operations where needed.

Filesystem relevance is through device support: RTC, UART, PIC, PCI config, and raw arch device files all depend on these accessors.

Notable risks: byte ordering differs between scalar and string operations; correctness is tied to Raven/MTX I/O-window mapping.
