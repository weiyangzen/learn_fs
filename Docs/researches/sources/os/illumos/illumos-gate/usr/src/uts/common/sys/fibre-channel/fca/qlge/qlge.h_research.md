# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlge/qlge.h

## Role

`qlge.h` is the main private driver header for the illumos `qlge` QLogic Ethernet driver. It connects illumos DDI/MAC/GLD facilities with QLogic hardware definitions from `qlge_hw.h`, debug macros from `qlge_dbg.h`, and version defaults from `qlge_open.h`.

## Major Definitions

The file defines:
- Driver identity (`ADAPTER_NAME`), boolean compatibility values, endian conversion macros, helper word/byte extraction macros, carrier update macros, and common return codes.
- Solaris compatibility/timer/DMA constants.
- DMA descriptor wrapper `struct dma_info` and helper macros for sync, virtual address access, and zeroing.
- Initialization step flags used during attach/setup/teardown.
- TX/RX limits for scatter/gather, LSO, copy thresholds, VLAN fallback constants, checksum offsets, and timeout thresholds.
- MAC driver states such as init, attached, started, bringdown, stopped, detach, and suspended.
- Soft reset request flags.
- Ioctl reply enum values used by STREAMS/ioctl handlers.
- Link speeds, multicast and unicast address containers, kstat index values, loopback modes, and flash-image search states.

Queue and ring structures include:
- `bq_desc` for receive buffer descriptors and recycle callbacks.
- `tx_ring_desc` for TX queue entries, DMA handles, copy buffers, OALs, and packet metadata.
- `tx_ring` for work queue state, locks, producer/consumer indexes, doorbell registers, statistics, and queue-stop state.
- `rx_ring` for completion queue state, interrupt routing, receive statistics, large/small buffer queues, producer/consumer indexes, free/in-use descriptor rings, and polling/copy counters.
- `intr_ctx` for interrupt handler association, masks, and in-flight handler counts.
- `tx_buf_desc` for transmit buffer address/length descriptors.

The central `qlge_t` soft-state structure contains:
- DDI device, PCI, access-handle, register, and fault-management state.
- Interrupt handles and priorities.
- MAC registration handles, kstats, and GLD statistics.
- Adapter mutexes, timers, power state, function identifiers, link state, MTU, duplex, pause, loopback, DCBX, and LSO state.
- Multicast/unicast address state.
- Soft interrupt handles for MPI events and resets.
- Extended ioctl staging buffers and MPI core-dump storage.
- Mailbox synchronization fields, firmware/version/port config data, and ioctl DMA buffers.
- Flash layout, VPD, NIC configuration, and flash description state.
- TX/RX rings, coalescing settings, copy thresholds, RSS/ring counts, polling counters, and optional buffer-usage tracking.

## Interfaces

The header declares functions from multiple `qlge` source files:
- Register access, waits, PCI dumps, descriptor dumps, firmware dumps, GLD setup, chip/loop ioctls, and binary core dumps.
- Delay, semaphore locking, initialization, start/stop, multicast/promiscuous updates, hardware stats, TX/RX paths, doorbell access, MAC address register programming, XGMAC reads, interrupt control, polling, hashing, atomics, timers, and route initialization.
- Flash locking, flash load/dump/VPD/parameter helpers.
- MPI interrupt handling, MPI reset, firmware state/version, link status, mailbox tests, port config, loopback/pause, LED config, SFP dump, IDC request, flash tests, processor data access, RISC RAM access, and system error triggers.
- Core dump and debug printing helpers.
- Unicast MAC setup and fault-management helpers.

## Integration Notes

`qlge.h` is the driver’s coordination point. It is not a hardware ABI by itself; it composes illumos networking, DMA, interrupt, kstat, fault-management, mailbox, flash, and ring state around the fixed layouts in `qlge_hw.h`.
