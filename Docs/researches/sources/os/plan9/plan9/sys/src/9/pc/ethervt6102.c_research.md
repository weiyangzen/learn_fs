# File Research: sources/os/plan9/plan9/sys/src/9/pc/ethervt6102.c

VIA VT6102 Fast Ethernet / Rhine II and Rhine III driver, registered as `"vt6102"` and `"rhine"`. It uses PCI I/O ports, MII helpers, and chained descriptors with cache-line-aligned storage.

The file defines VIA Rhine registers, RX/TX config/control bits, interrupt bits, MII and EEPROM bits, descriptor layout, descriptor status/control flags, ring sizes (`Nrd=64`, `Ntd=64`), receive buffer size, and transmit bounce-copy size. `Ctlr` stores PCI identity, I/O port, MAC address, attach allocation, cache-line size, RX/TX descriptor rings, TX lock/head/tail/use count, command/interrupt state, MII state/link rendezvous, and RX/TX/stat counters.

`vt6102pci()` scans PCI Ethernet class devices for VIA IDs `1106:3065` and `1106:3106`, reserves I/O BAR0, allocates a controller, derives descriptor alignment from PCI cache-line size, rejects too-small alignment, initializes TX FIFO threshold, calls `vt6102reset()`, enables bus mastering, and queues the controller. `vt6102pnp()` selects an inactive controller, populates `Ether`, sets speed to 100 Mbps, and installs callbacks.

Reset starts with `vt6102detach()`, which clears power-management/WOL state for newer revisions and soft-resets the controller. `vt6102reset()` reloads EEPROM, reads the MAC address, configures DMA and RX/TX FIFO thresholds, enables broadcast/all-multicast receive, sets multicast filters to all ones, clears TX loopback/threshold bits, allocates `Mii`, wires `vt6102miimir()`/`vt6102miimiw()`, and probes PHYs. Autonegotiation call is present but commented out.

`vt6102attach()` allocates descriptor and TX bounce-buffer memory, constructs a circular RX descriptor chain with aligned receive blocks and a circular TX descriptor chain, programs RX/TX descriptor base registers, interrupt mask, and command register, then starts a link kernel process. RX descriptors point to allocated blocks and are owned by NIC except for the terminal descriptor setup.

TX completion and enqueue are handled together in `vt6102transmit()`. It frees completed descriptors, records TX error statistics, handles abort/invalid/underflow cases by waiting for TX engine shutdown and restarting descriptor address, then dequeues blocks. If packet data is not 4-byte aligned, it copies a prefix into a per-descriptor bounce buffer and may split the packet across two descriptors; aligned packets use one descriptor. The function tracks aligned/split/copied counts and requests an interrupt when the ring nears full.

`vt6102receive()` walks completed RX descriptors, records RX error bits, otherwise allocates a replacement block, subtracts Ethernet CRC from length, delivers the old block to `etheriq()`, installs the new block, and re-links descriptor ownership through the previous descriptor. `vt6102interrupt()` masks interrupts, acknowledges status, handles link, RX, and TX causes, adjusts TX FIFO threshold upward on underflow, calls receive/transmit handlers, panics on unexpected unhandled bits, and restores the interrupt mask.

`vt6102lproc()` waits on source-change interrupts, calls `miistatus()`, updates the full-duplex bit in the command register, reenables link interrupt, and sleeps. Promiscuous mode toggles `Prom`; multicast is coarse because all-multicast is already enabled. `vt6102ifstat()` reports RX/TX error counters, descriptor/cache stats, interrupt/link counters, TX alignment stats, threshold, and PHY registers.

Notable risks: comments note unresolved link interrupt behavior, incomplete init/reset organization, and untested TX FIFO threshold adjustment. Multicast filtering accepts all multicast. Autonegotiation is not actively started in reset.
