# File Research: sources/os/linux/linux/fs/smb/smbdirect/connect.c

Implements the client-side SMB Direct connection path. It drives RDMA address resolution, route resolution, QP creation, `rdma_connect_locked()`, SMB Direct negotiate request send, negotiate response receive, and final transition to connected state.

Key entry points:
- `smbdirect_connect()` validates that the socket is still `CREATED`, installs the connect RDMA CM handler, and starts address resolution against the destination.
- `smbdirect_connect_resolve_addr()` and `smbdirect_connect_resolve_route()` issue asynchronous RDMA CM resolution calls and set `expected_event`.
- `smbdirect_connect_rdma_connect()` validates FRWR support and optional IB/iWARP restrictions, selects MR type (`IB_MR_TYPE_MEM_REG` or `IB_MR_TYPE_SG_GAPS`), clamps responder resources and FRMR depth to device capabilities, creates the QP, prepares iWARP private data if needed, calls `rdma_connect_locked()`, and starts the RDMA-connect timeout.
- `smbdirect_connect_rdma_event_handler()` advances the RDMA CM state machine through `ADDR_RESOLVED`, `ROUTE_RESOLVED`, and `ESTABLISHED`; on establishment it normalizes peer initiator/responder resources for iWARP versus non-iWARP devices and starts SMB Direct negotiation.
- `smbdirect_connect_negotiate_start()` creates memory pools, initializes send batch/local credits, posts a receive for the negotiate response, sends `struct smbdirect_negotiate_req`, and starts the negotiate timeout.
- `smbdirect_connect_negotiate_recv_done()` queues response parsing in workqueue context after DMA-syncing the receive buffer.
- `smbdirect_connect_negotiate_recv_work()` validates `struct smbdirect_negotiate_resp`, applies negotiated send/receive/read-write limits, creates the client MR list, posts data-transfer receive buffers, and marks negotiation done.
- `smbdirect_connect_sync()` wraps async connect plus `smbdirect_connection_wait_for_connected()`.

Important state and invariants:
- Client status sequence is `CREATED -> RESOLVE_ADDR_NEEDED/RUNNING -> RESOLVE_ROUTE_NEEDED/RUNNING -> RDMA_CONNECT_NEEDED/RUNNING -> NEGOTIATE_NEEDED/RUNNING -> CONNECTED`.
- RDMA CM errors are converted to connection errno values, with device removal mapped to `-ENETDOWN` and rejected events to `-ECONNREFUSED`.
- iWARP reports peer RDMA depths from a different perspective than RoCE/IB in this path; the handler swaps fields before shared resource negotiation.
- The negotiate response must grant nonzero send credits and request nonzero receive credits; size fields must meet SMB Direct minimums and fit the local advertised limits.
- Client-side RDMA read/write registration resources are created only after a successful negotiate response, because `max_read_write_size`, `max_frmr_depth`, and responder resources are negotiated there.

Dependencies:
- Uses `connection.c` for RDMA established handling, QP/mempools, receive posting/refill, send WR posting, MR list creation, and connected wait.
- Uses `socket.c` status/cleanup helpers.
- Uses `pdu.h` negotiate PDU definitions and `../common/smb2status.h` for success status validation.

Maintenance notes:
- Error paths after posting receives intentionally do not free posted receive buffers directly; cleanup relies on QP drain and completion handlers.
- The code assumes the first SMB payload seen after RDMA establishment is a negotiate response. If future versions add pre-negotiation messages, `recv_io.expected` and validation logic must be extended.
