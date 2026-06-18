# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_rxdma.h

## Purpose

`nxge_rxdma.h` defines the NXGE receive-DMA software state model and RXDMA entry points. It builds on `nxge_rxdma_hw.h` and NPI RXDMA APIs to represent receive buffer rings, receive completion rings, RX mailboxes, RX buffer loaning, polling, statistics, and channel initialization/recovery.

## Data Structures

The file defines operational defaults for RX clock divider, RED/WRED thresholds, RCR interrupt threshold/timeout, RX posting batch size, buffer alignment, and copy-threshold policy. `nxge_rxbuf_threshold_t` controls how aggressively packets are copied versus loaned; `nxge_rxbuf_type_t` maps software buffer classes to RCR hardware buffer-size codes.

`nxge_rx_ring_stats_t` is the main per-RDC counter block. It tracks packets/bytes/errors, multicast/broadcast/no-buffer counters, buffer allocation/reuse/drop counters, hardware event counters, and an `rdc_errlog_t` containing prefetch/shadow parity logs plus completion error type. `nxge_rdc_sys_stats_t` captures system-level RDMC FIFO/EOP/parity mismatches.

`rx_msg_t` is the per-receive-buffer state object. It includes DMA memory, lock, owning device/ring, spare/free/reference state, optional pass-up counter state, free callback, byte accounting, block sizing, usage counters, buffer pointer, priority, shifted address, pool flag, associated mblk, and bcopy policy.

`rx_rcr_ring_t` models a receive completion ring: DMA allocation, stats, poll flag, config registers, lock, indices, descriptor pointers, RBR linkage, interrupt timeout/threshold, MAC ring handle, generation number, byte accumulator, interrupt group/vector references, and started state.

`rx_rbr_ring_t` models a receive buffer block ring: descriptor DMA, `rx_msg_t` array, DMA buffer array, RBR config/kick/logical-page registers, ring indices, block and packet-buffer sizing, RCR backpointer, optional sun4v workaround mappings, thresholds, bcopy policy, reference count, state, and allocation type.

`rx_mbox_t`, `rx_rbr_rings_t`, `rx_rcr_rings_t`, `rx_mbox_areas_t`, and `rxdma_globals_t` aggregate mailbox/ring/global RXDMA state.

## Interfaces

The exported prototypes cover:

- Channel lifecycle: initialize/uninitialize all channels or one channel.
- RCR flush, reset, control/status setup, event-mask setup, and channel enable.
- 32-bit/64-bit hardware mode setup and RX hardware start.
- Ring fixup and channel repair.
- MAC polling enable/disable and receive polling.
- Register dumping, system error handling, and error injection.
- RX memory pool allocation/free and RX ring index lookup.

## Research Notes

This header is the software half of the RXDMA ABI. The highest-risk semantics are RX buffer loan/reference handling, `RBR_POSTING` to `RBR_UNMAPPING` transitions, RCR/RBR index wrap management, and coordination between interrupt mode and polling mode. The `RXBUF_START_ADDR` macro appears syntactically incomplete in the header as read, which may be hidden by non-use or historical build context.
