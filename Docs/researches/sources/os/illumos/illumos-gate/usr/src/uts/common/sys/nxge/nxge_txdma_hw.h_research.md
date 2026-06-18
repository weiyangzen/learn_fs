# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_txdma_hw.h

## Purpose

`nxge_txdma_hw.h` defines the transmit-DMA hardware ABI: logical page partitioning, addressing mode, packet descriptors, TX ring registers, event masks, control/status, mailbox format, error logs, packet header offload format, and debug/error-injection registers.

## Descriptor And Ring ABI

`tx_desc_t` is the 64-bit packet descriptor. It encodes source address, transfer length, gather pointer count, mark bit, and start-of-packet bit. `TX_MAX_GATHER_POINTERS` is 15, with a threshold of 8. The header documents a hardware bug that reduces max transfer length to 4076 and sets jumbo MTU at 9216.

TX ring registers configure descriptor base/length, head low, kick/tail, event mask, control/status, mailbox address high/low, prefetch state, ring error logs, interrupt debug, and control/status debug. `tx_rng_cfig_t`, `tx_ring_hdl_t`, and `tx_ring_kick_t` model base/length/head/tail/wrap fields.

## Events, Control, And Mailbox

`tx_dma_ent_msk_t` and `tx_cs_t` define event mask/control status bits for packet partition error, config partition error, NACK packet read, NACK prefetch, prefetch buffer parity/ECC error, ring overflow, packet size error, mailbox error, marker bits, stop-and-go, mailbox state, reset state, last mark, and packet count.

`txdma_mbh_t` and `txdma_mbl_t` split the mailbox address. `tx_dma_pre_st_t` exposes prefetch shadow head. `tx_rng_err_logh_t` / `tx_rng_err_logl_t` capture transmit ring error address, code, multiple-error flag, and error-present flag. `txdma_mailbox_t` is the 64-byte hardware mailbox image containing TX control/status, prefetch state, head, kick, error logs, and padding.

## Packet Header Offload Format

`tx_pkt_header_t` defines the 16-byte internal packet header's first 64-bit word: padding, total transfer length, L4 checksum stuff/start, L3 start, IP header length, VLAN, LLC, IP version, and checksum packet type. Constants define L4 operations for no-op, full checksum, payload checksum, and SCTP CRC32, plus packet types for TCP, UDP, SCTP, and no-op. `tx_pkt_hdr_all_t` adds the reserved second 64-bit word.

## Debug And Error Injection

The file defines parity-error injection for 24-channel and N2 16-channel variants, TDMC debug select, and TDMC training vector registers. Old scheduler/DRR/performance definitions remain under `#if OLD`.

## Research Notes

This file is central to TX data integrity. Audit-sensitive details include endian handling in descriptors, source address and transfer length masks, max transfer length enforcement, marker/interrupt semantics, write-one-to-clear control bits, and the relationship between software `tx_ring_t` indices and hardware head/tail/wrap fields.
