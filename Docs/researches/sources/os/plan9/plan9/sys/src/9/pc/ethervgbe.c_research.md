# File Research: sources/os/plan9/plan9/sys/src/9/pc/ethervgbe.c

VIA Velocity VT6122 gigabit Ethernet driver, registered as `"vgbe"`. Comments say register information came from the FreeBSD driver and list many TODOs: 64/48-bit DMA, autonegotiation, thresholds, dynamic ring sizing, link status changes, shutdown, promiscuous mode, error reporting, checksum offload, and jumbo frames.

The driver uses I/O-port access macros and fixed ring sizes (`RxCount=256`, `TxCount=256`, `RxSize=2048`). It defines Velocity command, EEPROM, MII, RX/TX, DMA, timer, configuration, and interrupt registers. `Ctlr` holds PCI device, port, init lock, debug flags, MII pointer, MAC address, RX/TX rings and block arrays, TX lock/count, and basic stats.

MII access is constrained to PHY address 1. `vgbemiir()`/`vgbemiiw()` write MII address/data/command registers and poll command bits until clear. `vgbereset()` soft-resets the controller, reloads EEPROM, reads MAC address registers, clears/masks interrupts, forces 32-bit address high registers to zero, starts the MAC, clears RX/TX queue run bits, enables RX/TX engines, allocates an MII structure, and probes PHY 1.

`vgbepci()` scans PCI Ethernet devices for VIA vendor/device `1106:3119`, requires I/O BAR0 with size 256, reserves the port, allocates a controller, and appends it to the controller list. `vgbepnp()` selects an inactive controller, calls `vgbereset()`, populates `Ether` fields, and installs attach/transmit/interrupt/ifstat/shutdown/control/multicast callbacks. Promiscuous callback exists but is not wired in.

`vgbeattach()` runs once. It allocates aligned RX and TX rings, allocates one RX block per RX descriptor through `vgbenewrx()`, programs RX MAC filtering for multicast/broadcast/unicast, loads RX ring base/count/index/residue, initializes DMA and TX MAC config, loads TX ring base/count/index, enables flow control, starts RX/TX queues, marks initialized, unmasks interrupts, and wakes the RX queue.

Receive completion scans the entire RX ring. `vgberxeof()` ignores descriptors still owned by hardware, accepts descriptors marked `Goodframe`, derives length from status, advances the stored block write pointer, passes it to `etheriq()`, increments RX stats, then returns descriptor ownership to hardware. The block is reused by setting `block->free = noop`, so ownership and lifetime depend on the networking stack returning it without actually freeing memory.

Transmit uses a single-fragment descriptor. `vgbetransmit()` starts from hardware `TxDscIdx`, finds free descriptors with no software block and no hardware ownership, dequeues blocks, stores them in `tx_blocks`, fills descriptor status/control and first fragment address/length, increments `tx_count`, and wakes the TX queue. `vgbetxeof()` scans TX descriptors, frees software blocks for descriptors no longer owned by hardware, updates stats, and wakes the queue if work remains.

`vgbeinterrupt()` masks interrupts, reads/acks `Isr`, filters to `Isr_Mask`, increments interrupt stats, optionally dumps decoded interrupt bits, calls RX/TX completion handlers, prints notable events, and on RX/TX DMA stall clears the global interrupt mask and returns. `vgbeifstat()` reports simple TX/TX-error/RX/intr counters. `vgbectl()` supports software reset/restart plus debug commands `dumpintr`, `dumprx`, `dumptx`, and `dumpall`.

Notable risks: RX blocks are reused with a no-op free routine and are not replaced after delivery, which requires careful external ownership expectations. Promiscuous mode is stubbed and not registered. Multicast is assumed already enabled. DMA address high registers are zeroed, so only 32-bit DMA is supported. Many TODOs remain in comments.
