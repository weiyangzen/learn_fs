# File Research: sources/os/plan9/9front/sys/src/9/pc/ether8169.c

## Purpose
Realtek RTL8169/8110/8168/8111/810x PCI/PCIe Gigabit/Fast Ethernet driver with MII support, descriptor rings, checksum flags, and hardware tally counters.

## Exposed Interface
- Link function: `ether8169link()`
- Registers:
  - `addethercard("rtl8169", rtl8169pnp)`

## Implementation Notes
- Supports multiple PCI IDs and many MAC hardware versions (`Macv01` through newer variants such as `Macv51`).
- `rtl8169pci()` scans PCI Ethernet devices, filters supported IDs, reserves I/O BARs, enables PCI, vets MAC version through TCR, halts the chip, and builds a controller list.
- `rtl8169pnp()` selects an inactive controller, fills `Ether` fields, reads MAC address if not overridden, installs hooks, and records initial link state.
- `rtl8169attach()` lazily allocates TX/RX rings, block arrays, and a 64-byte-aligned tally-counter block, enables bus mastering, registers interrupts, initializes hardware, initializes MII/PHY, and starts a reset helper kproc.
- Ring layout:
  - TX ring: 64 descriptors.
  - RX ring: 256 descriptors.
  - RX buffers allocated from a `Bpool` sized to rounded Ethernet MTU plus CRC.
- `rtl8169init()` resets the chip, clears/free old descriptors, replenishes RX buffers, configures C+ mode, descriptor base addresses, tally counters, TX/RX configuration, multicast hash, maximum packet size, coalescing, interrupt mask, and controller-specific RXDV gating.
- `rtl8169mii()` installs MII read/write callbacks using `Phyar`, wakes selected PHYs, obtains PHY revision, prints PHY/MAC info, resets PHY, and starts autonegotiation.
- `rtl8169transmit()` reclaims completed TX descriptors, queues blocks from `edev->oq`, writes descriptor physical addresses, marks ownership, and polls normal-priority queue.
- `rtl8169receive()` processes owned-back RX descriptors, replenishes low rings, validates first/last/error bits, strips CRC, records multicast/FIFO/checksum status, marks `Block` checksum flags, and passes packets to `etheriq()`.
- `rtl8169interrupt()` acknowledges ISR, records serious and recoverable interrupt counters, restarts on system/FIFO errors, processes RX/TX, and updates link on `Punlc`.
- `rtl8169ifstat()` dumps hardware tally counters through DMA, updates generic `Ether` counters, reports driver counters, and prints MII registers.
- `rtl8169multicast()` uses Ethernet CRC hash and reverses hash register byte order for PCIe variants.
- `rtl8169shutdown()` halts the controller.

## Filesystem Relevance
Network driver only, but it is a substantial PCI DMA descriptor-ring implementation. It is useful context for block/storage-style DMA patterns and Plan 9 device-driver resource management.

## Risks / Quirks
- Header notes undocumented “magic” register values and limited tuning/testing.
- Serious errors wake a reset kproc rather than fully recovering inline.
- Hardware-version handling is extensive and may reject unknown versions.
- `rtl8169ifstat()` can raise `Eio` if tally-counter DMA does not complete.
