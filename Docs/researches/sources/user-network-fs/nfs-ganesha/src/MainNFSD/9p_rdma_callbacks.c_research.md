<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_rdma_callbacks.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_rdma_callbacks.c

## Purpose
Provides Mooshika RDMA callbacks for 9P/RDMA sends, receives, errors, disconnects, and request execution. It adapts RDMA buffers into the shared 9P request queue and recycles output buffers.

## Important APIs, Types, And Functions
- `_9p_rdma_callback_recv()` allocates request data, attaches the receive buffer, records a flush hook, and dispatches work.
- `_9p_rdma_process_request()` validates the RDMA frame, calls `_9p_process_buffer()`, reposts receive buffers, and posts sends.
- `_9p_rdma_callback_send()` and `_9p_rdma_callback_send_err()` recycle output buffers.
- `_9p_rdma_callback_recv_err()` reposts receives while connected.
- `_9p_rdma_callback_disconnect()` delegates cleanup.

## Control Flow
Receive completion enqueues a request into the shared 9P worker pool. The worker waits for an output buffer, treats the received RDMA data as a 9P packet, checks header length, processes into the output buffer, reposts the input buffer, and posts a send. Send callbacks return output buffers to the outqueue and update stats.

## State And Persistence Behavior
State is transient RDMA transport, outqueue, receive/send buffers, memory registrations, connection refs, and flush hooks. No durable persistence.

## Dependencies And Integration Points
Integrates Mooshika, `DispatchWork9P`, `_9p_process_buffer`, server stats, health counters, and RDMA setup/cleanup code.

## Risks
- Receive callback reads the tag before validating packet size.
- Workers can block indefinitely waiting for output buffers.
- Send errors recycle without retry.
- TCP and RDMA differ in `_9pmsg` ownership expectations.

## Test Signals
Test valid frames, short frames, length mismatch, output-pool exhaustion, send/receive failures, disconnect during queued work, and flush-hook cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_rdma_callbacks.c -->
