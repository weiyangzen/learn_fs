# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_txdma.h

## Purpose

`nxge_txdma.h` defines the NXGE transmit-DMA software ring model, transmit message bookkeeping, statistics, mailbox/ring aggregates, and TXDMA entry points. It sits above `nxge_txdma_hw.h` and NPI TXDMA accessors.

## Ring And Buffer State

The file defines port DMA bitmap access, reclaim defaults, full-ring marker policy, transmit load-balancing modes, ring empty/full helpers, descriptor index increment, and default DRR weight.

`tx_msg_t` tracks one transmit message or premapped buffer: DMA/bcopy/DVMA flags, buffer DMA state, DMA handles, linked-list pointer, original mblk, message size, byte usage, and descriptor head/tail indices.

`nxge_tx_ring_stats_t` tracks packets/bytes/errors, initialization/no-buffer events, mailbox and hardware errors, start/nocanput failures, message duplication/allocation/DMA bind/descriptor failures, underruns, header/DDI/DVMA packet classes, max pending descriptors, jumbo packets, and a TXDMA ring error log from the hardware header.

`tx_ring_t` is the core TDC software state. It includes descriptor DMA, message ring, TX hardware config/status/mailbox/logical-page registers, TXC max-burst state, online/offline flags, locking, MAC ring handle, taskq, channel configuration pointer, ring size/chunks, software and hardware indices, pending descriptor count, queueing state, software queue head/tail, interrupt group, stats, DVMA ring state, and optional sun4v workaround mappings.

## Interfaces

The exported functions cover channel lifecycle, DMA common setup, reset, event mask setup, control/status setup, channel enable, packet header reservation, DMA block counting, descriptor reclaim, offload header fill, 32-bit/64-bit mode, hardware start/stop/restart, ring/channel fixup, hardware kick, register dumps, hang detection/recovery, reclaim of all rings, error injection, and TX memory pool allocation/free.

## Research Notes

This header defines the transmit fast-path contract between MAC, DMA mapping, descriptor rings, and hardware. Key risk points are descriptor wrap/full logic, concurrent reclaim versus send, DVMA ring accounting, offline state transitions, hang detection thresholds, and correct construction of TX packet headers for checksum offload.
