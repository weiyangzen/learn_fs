# File Research: sources/os/plan9/9front/sys/src/9/pc/etheryuk.c

Implements the Marvell Yukon-2 family Ethernet driver, registered as `yuk`, covering several Marvell and D-Link PCI IDs.

Key elements:
- Supports devices listed in `vtab`, including `88e8040`, `88e8053`, `88e8055`, `88e8056`, `88e8057`, `88e8071`, `dge-560t`, `dge-550sx`, and `dge-550t`.
- Contains a large register map for PCI config, global CSR, GMAC, PHY, queues, prefetch units, RAM buffers, status rings, timers, and error sources.
- `Chipid` and `idtab` classify Yukon variants and feature flags such as gigabit, new PHY, advanced power, new little-endian checksum format, fiber, and RAM buffering.
- Uses hardware status ring entries represented by `Status`; rings are tracked by `Sring` with write/read pointers, count, mask, and descriptor array.
- `Ctlr` stores PCI state, MMIO views at byte/word/dword widths, ring state, TX/RX block ownership arrays, block pool, multicast list, feature/type/revision data, port number, MAC address, and per-worker rendezvous events.
- `scan()` discovers supported PCI devices and stores lightweight controller records; `setup()` maps MMIO, reads MAC address, allocates aligned status/TX/RX rings, resets and initializes the hardware, and enables bus mastering.
- `identify()` derives Yukon type and revision from chip registers and feature tables, then detects fiber PHYs from PMD type.
- `reset()` disables ASF, resets bus/master state, powers hardware, configures timers/status rings, clears descriptor ownership, resets statistics/status engines, and handles advanced power-management quirks.
- `macinit()` resets MAC/PHY, powers PHY, initializes autonegotiation, clears MIB counters, configures collision/flow/RX/serial mode, programs MAC addresses, initializes FIFO/RAM behavior, and resets per-port RX/TX init state.
- `phyinit()` configures PHY-specific settings, autonegotiation advertisements, gigabit/fiber controls, FE+ workarounds, and PHY interrupt masks.
- `raminit()` partitions on-chip RAM between RX and TX queues when available, otherwise configures FIFO thresholds/store-forward behavior.
- `tproc()` initializes TX ring and sends packets from `e->oq` by writing address and packet descriptors, including 64-bit address descriptors when needed.
- `rproc()` initializes RX ring, enables RX, then continually replenishes receive descriptors from a `Bpool`.
- `sring()` consumes the hardware status ring, dispatches RX checksum notifications, RX completion, and TX completion index updates.
- `rx()` matches RX completion status to an owned buffer, checks status/error flags, sets checksum flags from `cksum()`, and delivers good packets with `etheriq()`.
- `txcleanup()` frees transmitted packet blocks up to a completed hardware index and wakes the TX producer.
- `interrupt()` reads `Isrc2`, which masks interrupts, and wakes `iproc`; `iproc()` handles PHY link changes, hardware errors, queue errors, and status-ring events.
- Error handlers `hwerror()`, `macintr()`, and `eerror()` clear/diagnose hardware, MAC, and queue/prefetch problems, with optional descriptor dumps from `yukdump.h`.
- `multicast()` maintains a linked list of active multicast addresses and rebuilds the 64-bit GMAC hash filter.
- `ctl()` supports `debug` toggling and a `descriptorfu` diagnostic command.

Filesystem relevance: none directly. It is a complex Ethernet driver that demonstrates Plan 9 PCI/MMIO hardware setup, status-ring DMA, block-pool RX replenishment, PHY/autonegotiation management, and deferred interrupt processing.
