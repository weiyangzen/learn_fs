# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_txc_hw.h

## Purpose

`nxge_txc_hw.h` defines the transmit-controller hardware register ABI for NXGE/Neptune/NIU. It covers TXC port DMA enable masks, per-channel DRR parameters, global control/training/debug, port statistics, reorder and store-forward ECC controls/status/data, reorder state read/write controls, packet request counters, and TXC interrupt status/masks.

## Control And Scheduling Registers

The header defines `TXC_PORT_DMA_ENABLE_REG` plus 24-bit and N2 16-bit DMA-list layouts for binding TX DMA channels to TXC/ports. Offset macros compute per-port and per-channel FZC register addresses.

Core control registers include DMA max burst, DMA max length, global TXC control, N2 two-port control, training vector, debug select, max reorder depth per port, and per-port clear/stat controls. Bitfield unions provide endian-aware access to port enable bits, TXC enable, port enable, training vector, debug selector, and reorder limits.

## Statistics And ECC Diagnostics

`txc_pkt_stuffed_t` and `txc_pkt_xmit` expose packet assembly/reorder and packet/byte transmit counters. Reorder ECC and store-forward ECC sections each define control, status, and five data registers per port. The ECC control fields support disabling UE, forcing single/double-bit errors, and selecting first/second/last/all/alternate/one packet injection styles. ECC status fields expose clear, correctable/uncorrectable error, and ECC address.

Reorder state registers expose TIDs in use, duplicate TID, unused TID, transaction timeout, FIFO space/watermark state, and `txc_ro_ctl_t` for fail-state clearing, failure capture flags, state read/write address, and state read/write completion bits.

`txc_ro_states_t` and `txc_sf_states_t` aggregate these hardware snapshots for error logging by `nxge_txc.h`.

## Interrupts

TXC interrupt status bits include store-forward correctable/uncorrectable error, reorder correctable/uncorrectable error, reorder error, and packet assembly dead. The file defines normal and debug interrupt status registers, a four-port interrupt mask, and an N2 two-port interrupt mask.

## Research Notes

This header is pure register metadata. High-risk fields are port/channel offset calculations, N2 versus four-port masks, ECC injection controls, and read/write state-machine bits in `txc_ro_ctl_t`. Some macros appear to refer to nonlocal or typo-like names such as `TXC_STATE0_REG` in offset macros; callers must be checked before changing them.
