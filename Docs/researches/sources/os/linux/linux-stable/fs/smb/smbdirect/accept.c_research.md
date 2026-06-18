# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/accept.c

## Purpose
Server-side SMBDirect accept and negotiation path. It converts an RDMA CM connect request into a `struct smbdirect_socket`, accepts the RDMA connection, receives the client's SMBDirect negotiate request, and sends the negotiate response only after the listener accepts the socket.

## Main Flow
- `smbdirect_accept_connect_request()` initializes server-side RDMA resources for an incoming request:
  - clamps `initiator_depth` to device capability
  - negotiates iWARP/IRD/ORD values through `smbdirect_connection_negotiate_rdma_resources()`
  - validates send SGE limits and initializes credits in `smbdirect_accept_init_params()`
  - creates QP and send/recv memory pools
  - posts one receive buffer for `SMBDIRECT_EXPECT_NEGOTIATE_REQ`
  - calls `rdma_accept()` with RC connection parameters
  - starts the negotiate timeout timer
- `smbdirect_accept_negotiate_recv_done()` handles the receive completion for the negotiate request, DMA-syncs it, appends valid request buffers to the reassembly queue, and schedules work.
- `smbdirect_accept_negotiate_recv_work()` validates the request:
  - version range must include `SMBDIRECT_V1`
  - `credits_requested` must be nonzero
  - peer receive and fragmented sizes must meet SMBDirect minima
  - local `max_recv_size`, fragmented receive size, send size, fragmented send size, and receive credit target are adjusted from peer values
- If the socket still has a listener, it is moved from listener `pending` to `ready` and the listener waitqueue is woken. A success response is deliberately deferred until `smbdirect_socket_accept()`.
- `smbdirect_socket_accept()` waits for a ready socket, detaches it from the listener, marks it connected for the caller, and then calls `smbdirect_accept_negotiate_finish(nsc, 0)` to grant credits and send the negotiate response.
- `smbdirect_accept_negotiate_finish()` posts receive buffers for data-transfer PDUs, grants receive credits, builds a negotiate response, maps it for DMA, and posts an RDMA SEND.
- `smbdirect_accept_negotiate_send_done()` frees the send buffer, decrements pending sends, disconnects on failed/non-success NT status, otherwise calls `smbdirect_connection_negotiation_done()`.

## RDMA Event Handling
- `smbdirect_accept_rdma_event_handler()` expects `RDMA_CM_EVENT_ESTABLISHED`.
- On established:
  - calls `smbdirect_connection_rdma_established()`
  - transitions to `SMBDIRECT_SOCKET_NEGOTIATE_NEEDED`
  - queues negotiation work if the receive completion already arrived
- Error, reject, device removal, or unexpected events schedule centralized cleanup.

## Important Semantics
- A passive connection can finish low-level RDMA establishment before the negotiate receive completion, or vice versa. The code explicitly handles both ordering possibilities.
- Successful negotiate response is withheld until upper layer accept, preventing credit grant to an unaccepted connection.
- Unsupported SMBDirect version sends a negotiate response with `STATUS_NOT_SUPPORTED`; malformed sizes/credits abort the transport.
- `accept.c` depends heavily on `connection.c` for QP, memory pools, receive refill, send posting, and final connected transition.
