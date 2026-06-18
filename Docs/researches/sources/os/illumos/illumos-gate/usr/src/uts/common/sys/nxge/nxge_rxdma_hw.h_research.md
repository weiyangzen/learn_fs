# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_rxdma_hw.h

## Purpose

`nxge_rxdma_hw.h` is the receive-DMA hardware register and descriptor ABI for Neptune/NIU. It defines FZC/DMC register offsets, masks, shifts, endian-aware register unions, RBR/RCR descriptors, mailboxes, WRED/discard counters, parity/error logs, RDMC debug access, FIFO diagnostics, and receive packet header formats.

## Global RXDMA Registers

The file begins with function-zero control registers for RX clock divider, default port-to-RDC mapping, RDC table entries, 32-bit addressing mode, port DRR weights, port FIFO usage, logical page partitioning, and WRED random initialization. Most registers are 64-bit CSRs with meaningful fields in the low 32 bits and `_BIG_ENDIAN` conditional layouts.

Logical page support uses common page-valid, mask, value, relocation, and handle registers per channel. RED/WRED support defines per-RDC parameter and discard-count registers with window/threshold fields for normal and synchronized thresholds.

## Ring And Descriptor ABI

`rx_desc_t` is the receive buffer block descriptor containing the posted block address. `rcr_entry_t` is the 64-bit completion descriptor containing buffer address, packet buffer size code, L2 length, DCF error, RX error code, promiscuous/noport flags, zero-copy flag, packet type, and multi-block indication.

The RBR registers configure descriptor base/length, three packet buffer sizes and valid bits, block size, kick count, status queue length/overflow, and hardware head. The RCR registers configure descriptor base/length, interrupt timeout/threshold, queue status, tail pointer, event mask, control/status, flush, and error logging.

The RCR error classes include no error, L2 error, L4 checksum error, FFLP soft error, ZCP soft error, and reserved values. Packet type values identify UDP, TCP, SCTP, or other.

## Error, Mailbox, And Debug State

`rx_dma_ent_msk_t` and `rx_dma_ctl_stat_t` describe the RXDMA interrupt mask and control/status bits. Events include config/RBR log page errors, RBR full/empty, RCR full/inconsistent, config errors, shadow full, pre-empty, WRED and port drops, prefetch/shadow parity, RCR timeout/threshold, data FIFO errors, ACK/response/byte-enable errors, and RBR timeout. `RX_DMA_CTL_STAT_WR1C` identifies write-one-to-clear bits.

`rxdma_mailbox_t` lays out the 64-byte mailbox image: control/status, RBR status/head, RCR tail/status, and reserved padding. `rx_disc_cnt_t` and `red_disc_cnt_t` count discards with overflow flags. `rdmc_par_err_log_t`, `rdmc_mem_addr_t`, `rdmc_mem_data_t`, and `rdmc_mem_access_t` support parity log and internal RDMC memory access. RX control/data FIFO state reports IPP/ZCP EOP errors and ID mismatch. A training vector register is also exposed.

## Packet Header Formats

The file defines the two-byte RX packet header format 0 with input port, MAC check, class, VLAN, LLC/SNAP, noport, bad IP, TCAM hit, and transfer-zone validity. It also defines the 18-byte format 1 as byte-sized unions for TCAM match, hash hit/index/value, zero-copy flow ID, user data, and reserved fields, aggregated as `rx_pkt_hdr1_t`.

## Research Notes

This is a dense hardware ABI file. Maintenance risks include incorrect bit masks, duplicated/misspelled mask macros, endian layout mistakes, confusing address low/high split handling, and incorrect write-one-to-clear behavior. RX correctness depends on strict agreement between this header, NPI register accessors, and `nxge_rxdma.h` ring bookkeeping.
