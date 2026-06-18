# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_buf.h

This header defines the Emulex OneConnect Ethernet driver's buffer-management layer: DMA buffer descriptors, queue ring helpers, receive-buffer descriptors, transmit-buffer descriptors, and cache-management prototypes.

Key contents:
- Queue index helper `GET_Q_NEXT()` and ring-state macros for pending/free/full/empty state, producer/consumer pointer movement, and virtual/physical item lookup.
- TX mapping limits: `OCE_MAX_TX_HDL`, `OCE_MAX_TXDMA_COOKIES`, `OCE_TX_MAX_FRAGS`.
- `oce_addr64_t`, an endian-aware 64-bit physical address accessor split into high/low 32-bit fields.
- `oce_dma_buf_t`, the common DMA allocation descriptor carrying kernel VA, device PA, access handle, DMA handle, size/offset/length, and page count.
- DMA buffer access/sync macros, including `DBUF_PA`, `DBUF_VA`, `DBUF_DHDL`, and `DBUF_SYNC`.
- `oce_ring_buffer_t`, the generic DMA-backed ring descriptor shared by hardware queues.
- Receive buffer descriptor `oce_rq_bdesc_t`, including DMA buffer, receive queue backpointer, fragment address, STREAMS `mblk_t`, free routine, and reference count.
- Transmit copy/mapped buffer descriptors and WQE descriptor structures: `oce_wq_bdesc_t`, `oce_wq_mdesc_t`, `oce_handle_t`, and `oce_wqe_desc_t`.
- WQE entry type enum for header, mapped, copy, and dummy WQEs.
- Packed receive-buffer headroom header `oce_rq_buf_hdr_t` and `OCE_RQE_BUF_HEADROOM`.
- Prototypes for RQ/WQ cache creation/destruction, WQE descriptor constructors/destructors, mapped-DMA-handle caches, and DMA page-list extraction.

Dependencies:
- Includes `sys/ddidmareq.h`, `oce_io.h`, and `oce_utils.h`.
- Uses `struct oce_rq`, `struct oce_wq`, `struct oce_nic_frag_wqe`, `struct phys_addr`, STREAMS `mblk_t`, DDI DMA/access handles, and the driver's `OCE_LIST_NODE_T`.

Research notes:
- This is a low-level memory contract for the OCE transmit/receive paths. Correctness depends on DMA handle lifetime, ring index accounting, and physical-address packing.
- The file is tightly coupled to `oce_io.h` queue definitions and `oce_hw_eth.h` NIC WQE/RQE formats.
- The packed RX buffer header and 18-byte headroom are part of receive packet layout assumptions.
