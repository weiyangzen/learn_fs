# File Research: sources/os/plan9/9front/sys/src/9/mtx/ether2114x.c

This is a full PCI Ethernet driver for DEC 2114x/Tulip-family controllers and related PNIC variants. It handles PCI discovery, SROM parsing, MII management, media selection, descriptor-ring setup, transmit, receive, interrupts, statistics, and generic Plan 9 Ethernet registration.

The main state is `Ctlr`, containing PCI/device identity, SROM/media/PHY state, CSR6 mode bits, interrupt mask, receive and transmit descriptor rings, locks, queued setup packet, link speed, and detailed error counters. `Des` models RX/TX descriptors with status/control/DMA address/block pointer.

Driver registration is `ether2114xlink`, adding card names `21140` and `2114x`. `dec2114xpci` scans PCI devices, matches supported IDs, allocates I/O space, resets the device, reads SROM, and links controllers. `reset(Ether*)` binds a controller to an `Ether`, handles MAC/media options, sets DMA bus mastering, initializes rings, installs callbacks, and enables interrupts.

RX/TX operation uses `ctlrinit`, `txstart`, `transmit`, and `interrupt`. The interrupt handler acknowledges CSR5 status, processes receive descriptors into `etheriq`, handles TX completion/errors, raises thresholds on underflow, and tops up TX descriptors.

Filesystem relevance is indirect but important: Plan 9 network stacks and network filesystems depend on this driver for connectivity; the generic `etherif` exports network interfaces as device files.

Notable risks: one line hardcodes `ether->irq = 2` with an explicit complaint comment instead of using PCI interrupt line; media/SROM decoding is partial; some card-specific fake leaves are embedded; DMA coherency depends on `coherence()` and `PCIWADDR`.
