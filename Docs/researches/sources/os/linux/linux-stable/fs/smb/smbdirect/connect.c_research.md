# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/connect.c

## Purpose
Client-side SMBDirect connection establishment. It drives RDMA address resolution, route resolution, RDMA connect, SMBDirect negotiate request/response exchange, and synchronous wait helper.

## Main Flow
- `smbdirect_connect()` validates a newly created socket, captures any bound source address, installs the connect RDMA event handler, and starts `rdma_resolve_addr()`.
- `smbdirect_connect_rdma_event_handler()` advances the state machine:
  - `ADDR_RESOLVED` -> `smbdirect_connect_resolve_route()`
  - `ROUTE_RESOLVED` -> `smbdirect_connect_rdma_connect()`
  - `ESTABLISHED` -> RDMA resource negotiation and SMBDirect negotiate start
- `smbdirect_connect_rdma_connect()`:
  - checks FRWR support
  - enforces optional IB-only or iWARP-only flags
  - selects MR type (`IB_MR_TYPE_SG_GAPS` when supported, otherwise `IB_MR_TYPE_MEM_REG`)
  - clamps `max_frmr_depth` and responder resources to device limits
  - creates QP
  - sends legacy IRD/ORD private data for iWARP
  - calls `rdma_connect_locked()`
  - starts a connect timeout timer
- `smbdirect_connect_negotiate_start()`:
  - creates send/recv memory pools
  - initializes batch/local send credits
  - posts one receive buffer for the negotiate response
  - allocates a send buffer containing `struct smbdirect_negotiate_req`
  - fills version, credit request, send size, receive size, and fragmented receive size
  - DMA maps and sends the request
  - starts negotiate timeout
- `smbdirect_connect_negotiate_recv_done()` handles the response receive completion, syncs DMA, stores valid responses in the reassembly queue, and schedules work.
- `smbdirect_connect_negotiate_recv_work()` validates response fields:
  - negotiated version must be `SMBDIRECT_V1`
  - NT status must be success
  - peer receive and fragmented sizes must meet SMBDirect minima
  - both requested and granted credits must be nonzero
  - peer preferred send size must fit local receive size
  - resulting max read/write size must be at least one page
- After validation it updates local negotiated parameters, creates the MR list, switches receive buffers to data-transfer completion handling, refills receive buffers, and calls `smbdirect_connection_negotiation_done()`.
- `smbdirect_connect_sync()` wraps `smbdirect_connect()` and `smbdirect_connection_wait_for_connected()`.

## iWARP Handling
- iWARP reports peer initiator/responder values from a different perspective than non-iWARP transports. The established event path swaps values before negotiation.
- Legacy iWARP private data is passed to shared resource negotiation.

## Error Handling
- Any unexpected RDMA event/status maps to transport errors such as `-ECONNREFUSED`, `-ENETDOWN`, or event status, then schedules cleanup.
- `-ENODEV` logging is downgraded to info in synchronous wait paths.
