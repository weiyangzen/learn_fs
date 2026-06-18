# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/connection.c

## Purpose
Core SMBDirect connection engine shared by client and server. It manages QP/CQ/PD lifecycle, negotiated connected transition, send/receive credits, SMBDirect data-transfer PDUs, keepalive, receive reassembly, send batching, and iterator-to-SGE DMA mapping.

## RDMA/QP Lifecycle
- `smbdirect_connection_qp_event_handler()` schedules cleanup on fatal QP/CQ events.
- `smbdirect_connection_rdma_event_handler()` is installed after RDMA establishment and expects `RDMA_CM_EVENT_DISCONNECTED`. It handles normal disconnect and device removal by forcing status toward `DISCONNECTED` and draining the QP.
- `smbdirect_connection_rdma_established()` logs local/remote endpoints, installs the steady-state event handler, and changes expected CM event to disconnect.
- `smbdirect_connection_negotiation_done()` transitions from negotiating to connected, initializes receive-refill and immediate-send work handlers, and wakes waiters.
- `smbdirect_connection_create_qp()` computes QP capacity from send credits, receive credits, responder resources, and RDMA RW context needs, validates device CQ/WR/SGE limits, allocates PD/CQs, and creates an RC QP.
- `smbdirect_connection_destroy_qp()` drains and destroys QP, CQs, and PD.

## Memory Pools
- `smbdirect_connection_create_mem_pools()` creates per-socket slab caches/mempools for:
  - send I/O objects sized to include a negotiate response-sized packet area
  - receive I/O objects sized to include `max_recv_size` user-exposable receive buffer
- It preallocates `recv_credit_max` receive buffers into the free list.
- `smbdirect_connection_destroy_mem_pools()` frees free-list receive buffers and destroys pools/caches.

## Receive Buffer Management
- `smbdirect_connection_get_recv_io()` pops from the free list unless the socket has an error.
- `smbdirect_connection_put_recv_io()` DMA-unmaps a posted receive buffer if needed, returns it to the free list, updates statistics, and queues refill work.
- `smbdirect_connection_post_recv_io()` DMA maps the receive packet area and posts one receive WR.
- `smbdirect_connection_recv_io_refill()` posts enough receive buffers to satisfy the peer's current requested target, records newly available credits, and returns the number of buffers posted.
- `smbdirect_connection_recv_io_refill_work()` can schedule an empty immediate send so newly available credits are advertised to the peer.

## Credit Handling
- `smbdirect_connection_grant_recv_credits()` moves posted receive availability into granted receive credits up to the current peer-requested target.
- Send path has three credit concepts:
  - batch credit: serializes a send batch
  - local credits: available local send WR capacity
  - remote send credits: peer-granted ability to send data-transfer PDUs
- `smbdirect_socket_wait_for_credits()` from `socket.c` underpins these waits.

## Send Path
- `smbdirect_connection_send_single_iter()` builds one SMBDirect data-transfer PDU:
  - validates connected state and iterator direction
  - waits for batch/local/remote send credits
  - optionally grants receive credits
  - allocates a send buffer
  - maps header and payload SGEs
  - sets `credits_requested`, `credits_granted`, flags, offsets, lengths, and remaining length
  - optionally sets `SMBDIRECT_FLAG_RESPONSE_REQUESTED` for keepalive
  - posts immediately or appends to a batch
- `smbdirect_connection_send_iter()` expects an RFC1002-style 4-byte length prefix, validates fragmented send size, sends fragments through a batch, flushes the batch, and waits for pending sends to drain.
- `smbdirect_connection_send_batch_flush()` chains WRs, optionally converts the first to `IB_WR_SEND_WITH_INV`, signals the last WR, and posts the chain.
- `smbdirect_connection_send_io_done()` frees sibling send buffers and the signaled buffer, restores local credits, wakes waiters, and schedules cleanup on failed completions.
- `smbdirect_connection_send_immediate_work()` sends an empty data-transfer PDU for keepalive/credit advertisement.

## Receive/Reassembly Path
- `smbdirect_connection_recv_io_done()` parses incoming data-transfer PDUs:
  - validates completion opcode/status
  - refreshes keepalive timer
  - validates minimal header length, data offset alignment, bounds, and fragmented receive size
  - updates peer requested credits and locally usable send credits from `credits_granted`
  - handles response-requested keepalive flag
  - tracks first segment and full-packet state
  - queues payload buffers on the reassembly list or returns empty buffers
- `smbdirect_connection_reassembly_append_recv_io()` appends buffers and updates `data_length` after a write barrier so lockless readers can observe consistent queue metadata.
- `smbdirect_connection_recvmsg()` copies reassembled payload to a destination `msghdr` iterator:
  - returns a synthetic RFC1002 length when upper layer asks for 4 bytes at the first segment
  - copies partial or full segments
  - returns consumed buffers to the free list
  - waits interruptibly for enough data when needed

## Keepalive
- `smbdirect_connection_idle_timer_work()` treats pending/sent keepalive as timeout, otherwise schedules a response-requested empty message.
- Incoming data resets keepalive state and reschedules the interval timer.
- Empty sends are also used to advertise receive credits without payload.

## Iterator Mapping
- `smbdirect_map_sges_from_iter()` supports `ITER_BVEC`, `ITER_KVEC`, and `ITER_FOLIOQ` sources.
- `smbdirect_map_sges_from_bvec()`, `_kvec()`, and `_folioq()` map pages into IB SGEs without pinning/refcounting; callers must ensure iterator backing lifetime.
- On mapping failure, newly mapped SGEs are unmapped before returning.

## Public Exports
Exports connected-state helpers, wait helper, batch flush/init, send helpers, recvmsg, and lower-level send-wait functions through GPL symbols where marked.
