# File Research: sources/os/plan9/plan9/sys/src/9/omap/etherif.h

Defines the generic Ethernet controller structure and helper declarations for OMAP Ethernet drivers.

Key points:
- Sets `MaxEther=4` and `Ntypes=8`.
- Defines `Ether` as an `RWlock`, embedded `ISAConf`, controller number, min/max MTU, embedded `Netif`, and hardware callback pointers.
- Hardware callbacks include attach, detach, transmit, interrupt, ifstat, control, power, and shutdown.
- Stores hardware-private `ctlr`, MAC address `ea`, mapped address, IRQ, and output queue.
- Declares shared helper functions: `etheriq()`, `addethercard()`, `ethercrc()`, and `parseether()`.
- Defines ring helper macros `NEXT()` and `PREV()`.

Dependencies and interactions:
- Included by `devether.c`, `ether9221.c`, and platform arch code.
- Extends Plan 9 `netif` structures from `../port/netif.h`.

Research relevance:
- Small contract header between generic Ethernet device code and hardware Ethernet drivers.
