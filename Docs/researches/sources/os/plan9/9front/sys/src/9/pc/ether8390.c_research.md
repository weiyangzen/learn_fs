# File Research: sources/os/plan9/9front/sys/src/9/pc/ether8390.c

Shared National Semiconductor DP8390/DP83901/DP83902 and clone Ethernet controller core.

Primary role:
- Provides common NIC logic for board-specific 8390/NE2000-style drivers, including remote DMA, shared-memory handling, RX ring processing, transmit, interrupt handling, multicast hash filters, and reset/attach callbacks.

Key interfaces:
- `dp8390reset(Ether*)`: initializes the core and installs generic Ethernet callbacks.
- `dp8390read(Dp8390*, void*, ulong, ulong)`: reads adapter RAM through remote DMA.
- `dp8390getea(Ether*, uchar*)`: reads station address registers.
- `dp8390setea(Ether*)`: writes station address registers.

Important behavior:
- `dp8390getea()`/`dp8390setea()` switch to register page 1, access PAR registers, then restore the command register.
- `_dp8390read()` and `dp8390write()` use DP8390 remote DMA; `dp8390write()` supports the dummy remote-read workaround used by some clones.
- `ringinit()` programs receive page start/stop/boundary/current pointers.
- `receive()` walks the card receive ring, reads the DP8390 packet header, derives length from page pointers, validates ring state, handles wraparound copies, allocates a software block, and queues good packets.
- `txstart()` copies a queued packet into adapter memory or remote DMA, programs transmit byte count, starts TX, and marks `txbusy`.
- `overflow()` implements the DP8390 datasheet overflow-recovery sequence.
- `interrupt()` masks interrupts while processing, handles overflow, RX, TX, and counter-overflow events, then restores the interrupt mask.
- `setfilter()`, `promiscuous()`, and `multicast()` maintain receive mode plus the multicast address registers using CRC hash bits and per-bit reference counts.
- `attach()` clears pending interrupts, enables wanted interrupts, sets receive filter mode, and exits loopback into normal transmit mode.
- `disable()` stops the chip and waits for reset status with a probe-safe timeout.

External requirements:
- Board-specific code must provide the `Dp8390` structure from `ether8390.h`, port/data/memory layout, interrupt/port values, and usually station address discovery.

Research notes:
- The code supports both remote-DMA I/O-port boards and shared-memory boards through `ctlr->ram`.
- Ring corruption causes a diagnostic print and ring reinitialization.
- Multicast is more precise than several newer drivers because it tracks hash-bit reference counts.
