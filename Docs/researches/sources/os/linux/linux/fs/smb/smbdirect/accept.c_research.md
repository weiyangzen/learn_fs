# File Research: sources/os/linux/linux/fs/smb/smbdirect/accept.c

Implements the server-side SMB Direct accept path after `listen.c` has received an RDMA CM connect request and created an accepting child socket. It initializes responder parameters, creates the QP and memory pools, posts the first receive buffer for the SMB Direct negotiate request, calls `rdma_accept()`, handles `RDMA_CM_EVENT_ESTABLISHED`, validates the negotiate request, and sends the negotiate response.

Key entry points:
- `smbdirect_accept_connect_request()` transitions a child socket from `CREATED` to `RDMA_CONNECT_RUNNING`, negotiates RDMA initiator/responder resources from RDMA CM private data, sets server-side send/local/RDMA RW credits, creates QP/mempools, posts the negotiate receive, and starts the negotiate timeout.
- `smbdirect_accept_negotiate_recv_done()` is the CQ completion for the negotiate request. It validates CQ status/opcode, DMA-syncs the receive buffer, appends valid-sized requests to the reassembly queue, and defers protocol parsing to workqueue context.
- `smbdirect_accept_negotiate_recv_work()` parses `struct smbdirect_negotiate_req`, validates version, credits, receive size, and fragmented size, updates negotiated socket parameters, then either moves listener-owned children to the listener ready queue or calls `smbdirect_accept_negotiate_finish()` directly for non-listener accepted sockets.
- `smbdirect_accept_negotiate_finish()` prepares data-transfer receive buffers, grants receive credits, constructs `struct smbdirect_negotiate_resp`, DMA maps it, posts an `IB_WR_SEND`, and relies on send completion to finalize negotiation.
- `smbdirect_socket_accept()` waits for a ready child, removes it from the listener ready queue, marks it connected for the caller, then sends the deferred negotiate response that grants the client credits.

Important state and invariants:
- The server delays a successful negotiate response for listener children until userspace/kernel frontend calls `smbdirect_socket_accept()`. This prevents granting peer credits before the application accepts the socket.
- `sc->recv_io.expected` gates the receive completion path: negotiate request first, then data-transfer receives after successful negotiation.
- Some drivers can deliver the negotiate receive completion before `RDMA_CM_EVENT_ESTABLISHED`; the code handles this by initializing `sc->connect.work` in the receive completion and queueing it only once the status reaches `NEGOTIATE_NEEDED`.
- Invalid protocol version results in a negotiate response with `STATUS_NOT_SUPPORTED`; malformed sizes or zero credits trigger cleanup rather than a protocol-level negative response.
- `smbdirect_accept_negotiate_send_done()` frees the send buffer, decrements pending send count, disconnects on send failure, disconnects after non-success NT status, and calls `smbdirect_connection_negotiation_done()` on success.

Dependencies:
- Uses `connection.c` for QP/mempool creation, receive posting/refill, send WR posting, credit granting, reassembly queue helpers, RDMA established state, and negotiation completion.
- Uses `socket.c` cleanup/status machinery.
- Uses `pdu.h` SMB Direct negotiate PDU layouts and constants.
- Uses `../common/smb2status.h` for NT status values.

Maintenance notes:
- The code relies on careful ordering between RDMA CM callbacks, CQ callbacks, workqueue processing, and listener queue locking. Changes to statuses around `RDMA_CONNECT_RUNNING`, `NEGOTIATE_NEEDED`, and `NEGOTIATE_RUNNING` need to preserve the early-CQ-completion workaround.
- The accepted child temporarily remains on listener queues while negotiation parses; cleanup paths must continue to remove it and release listener ownership exactly once.
