# File Research: sources/os/plan9/9front/sys/src/9/pc/etherx550.c

Implements a compact Intel X553/X550-AT 10GBASE-T PCI Express Ethernet driver, registered as `iX550`.

Key elements:
- Matches Intel PCI ID `0x8086:0x15c8`.
- Defines MMIO register offsets for control/status, NVM readiness, interrupt control, RX/TX DMA rings, filters, multicast table, VLAN table, checksum control, link status, and MAC frame sizing.
- Uses Intel-style RX descriptors `Rd` and TX descriptors `Td`, plus arrays of `Block*` for packet ownership.
- `Ctlr` tracks PCI/MMIO mappings, descriptor rings, RX/TX indexes, interrupt masks, link/RX/TX rendezvous state, MAC address, multicast table, hardware stats, and speed counters.
- `scan()` maps BAR0 register space and BAR4 MSI-X space, enables PCI, resets the device, enables bus mastering, and stores controllers in `ctlrtab`.
- `detach()` saves the receive address, masks interrupts, issues a full reset, clears extra receive address slots, multicast table, VLAN filter table, and driver-load bit.
- `reset()` waits for EEPROM/configuration/DMA readiness, detaches/resets, clears stats, configures interrupt vector mapping, and programs interrupt throttling.
- `attach()` allocates aligned RX/TX descriptor memory and block pointer arrays, initializes RX/TX rings, marks driver load, and launches link, RX, and TX kernel processes.
- `rxinit()` configures broadcast accept, RX checksum, split/replication buffer size, max frame size, jumbo enable, descriptor base/length, RXDCTL, and RX enable.
- `replenish()` allocates page-aligned receive buffers and fills RX descriptors up to the hardware head.
- `rproc()` replenishes RX descriptors, waits for RX interrupts, consumes completed RX descriptors, sets IP checksum flags, and queues packets to `etheriq()`.
- `txinit()` zeros TX descriptors, programs TX base/length/head/tail, enables TX descriptor control and DMA TX.
- `transmit()` reclaims completed TX descriptors, sends up to eight queued packets per call, and enables TX interrupts when the ring is full or lock contention occurs.
- `interrupt()` masks interrupts, reads causes, wakes link/RX/TX processes, and reenables the remaining mask.
- `lproc()` tracks link status and speed based on `Links`.
- `multicast()` hashes multicast addresses into the 4096-bit multicast table but intentionally does not clear bits on removal because multiple addresses can collide.
- `ifstat()` reports hardware counters, speed transition counts, and RX ring state.

Filesystem relevance: none directly. This file is a PCIe 10GbE driver and illustrates modern Plan 9 Ethernet ring setup, deferred worker processing, checksum flag propagation, and multicast hash filtering.
