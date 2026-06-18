# File Research: sources/os/linux/linux/fs/smb/smbdirect/connection.c

Provides the core SMB Direct connected-session machinery: RDMA CM disconnect handling, QP/CQ/PD allocation, send and receive memory pools, credit accounting, keepalive handling, send batching, receive reassembly, and iterator-to-SGE DMA mapping.

Major areas:
- RDMA/QP lifecycle:
  - `smbdirect_connection_rdma_established()` switches the RDMA CM handler to the connected disconnect handler and expects `RDMA_CM_EVENT_DISCONNECTED`.
  - `smbdirect_connection_rdma_event_handler()` handles disconnect/device-removal events, schedules cleanup, and drains the QP.
  - `smbdirect_connection_create_qp()` validates device CQE/QP WR/SGE limits, allocates PD/CQs, accounts for RDMA RW work requests, and creates an RC QP.
  - `smbdirect_connection_destroy_qp()` drains and destroys QP, CQs, and PD.
- Memory pools:
  - `smbdirect_connection_create_mem_pools()` creates per-socket slab/mempool caches for send and receive IO objects and preallocates all receive buffers.
  - `smbdirect_connection_destroy_mem_pools()` returns free receive buffers and destroys pools/caches.
- Receive path:
  - `smbdirect_connection_post_recv_io()` DMA maps a receive buffer and posts an `ib_recv_wr`.
  - `smbdirect_connection_recv_io_done()` validates SMB Direct data-transfer headers, updates keepalive timer, adjusts receive/send credit accounting, handles response-requested keepalives, appends payload buffers to the reassembly queue, and schedules refills.
  - `smbdirect_connection_recv_io_refill()` posts missing receive buffers up to the peer-requested target and records newly available credits to grant.
  - `smbdirect_connection_recvmsg()` copies reassembled SMB payload data into a destination iterator and synthesizes an RFC1002 length header for first-segment 4-byte reads expected by upper layers.
- Send path:
  - `smbdirect_connection_send_single_iter()` waits for batch, local, and peer send credits; grants newly posted receive credits; builds a data-transfer PDU; maps payload iterator segments to SGEs; and posts or batches the send.
  - `smbdirect_connection_send_iter()` consumes the RFC1002 length header from the source iterator, enforces negotiated fragmented send size, sends fragments, flushes the batch, and waits for all pending sends.
  - `smbdirect_connection_send_batch_flush()` chains WRs, optionally turns the first WR into `IB_WR_SEND_WITH_INV`, signals the final WR, and releases the single batch credit.
  - `smbdirect_connection_send_io_done()` frees a signaled send and any sibling send IOs, restores local send credits, decrements pending count, and wakes waiters.
- Keepalive:
  - `smbdirect_connection_idle_timer_work()` converts idle interval expiry into an empty message request and treats pending/sent keepalive timeout as fatal.
  - `smbdirect_connection_send_immediate_work()` sends an empty data-transfer message for keepalive or credit-grant purposes.
- Iterator mapping:
  - `smbdirect_map_sges_from_iter()` supports `ITER_BVEC`, `ITER_KVEC`, and `ITER_FOLIOQ` source iterators, DMA maps page fragments into `ib_sge` entries, advances the iterator, and unmaps partial mappings on failure.

Important state and invariants:
- Receive credits represent posted receive buffers granted to the peer; send credits represent peer-granted permission to send data-transfer PDUs.
- There is exactly one send batch credit, serializing batch construction.
- Local send credits (`lcredits`) limit outstanding `IB_WR_SEND` WRs; they are returned by send completions.
- Reassembly queue updates use barriers: append updates list/queue length before data length; receive-side reads data length before queue metadata.
- `recvmsg()` assumes a single reader consumes from the front of reassembly while completions append at the back.
- Empty data-transfer messages are used both for keepalives and for granting receive credits.
- Iterator-to-SGE mapping does not pin pages; callers must provide iterator types whose backing pages are stable for the RDMA send lifetime.

Dependencies:
- Uses RDMA core verbs, RDMA CM, `rdma_rw_*` helpers, Linux pipe-like iterator primitives, and `folio_queue`.
- Shared structs and status/logging helpers come from `socket.h`/`internal.h`.
- PDU layouts come from `pdu.h`.

Maintenance notes:
- `smbdirect_connection_recvmsg()` contains subtle lockless/front-of-queue assumptions; any move toward multiple concurrent readers would require redesign.
- Send error unwinding restores credits manually; future changes to the credit model must audit all `goto` labels in `smbdirect_connection_send_single_iter()`.
- `ITER_FOLIOQ` mapping maps from `folio_page(folio, 0)` with an offset; changes to large-folio assumptions should be checked carefully.
