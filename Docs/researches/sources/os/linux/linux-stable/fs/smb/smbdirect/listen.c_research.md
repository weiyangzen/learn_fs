# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/listen.c

## Purpose
Listening socket setup and RDMA CM connect-request admission for SMBDirect.

## Listen Setup
- `smbdirect_socket_listen()`:
  - validates backlog and socket state
  - defaults backlog 0 to 1
  - transitions `CREATED` -> `LISTENING`
  - sets expected event to `RDMA_CM_EVENT_CONNECT_REQUEST`
  - installs `smbdirect_listen_rdma_event_handler()`
  - calls `rdma_listen()`
  - records backlog only after successful listen

## RDMA Event Handling
- `smbdirect_listen_rdma_event_handler()` handles only expected connect requests.
- For connect request events, it detaches the new CM ID from the listener context and installs a placeholder handler until the accepting socket owns it.
- Unexpected events or statuses schedule cleanup on the listener; for a new CM ID, error is returned so RDMA CM destroys it.

## Connect Request Admission
- `smbdirect_listen_connect_request()`:
  - validates FRWR support on the selected device
  - enforces listener port-range flags for IB/RoCE or iWARP only
  - counts pending and ready accepted sockets against backlog
  - creates an accepting socket for the new RDMA CM ID
  - copies logging and initial parameters from listener
  - copies kernel settings from listener
  - links new socket into listener `pending` list
  - calls `smbdirect_accept_connect_request()`
- On failure after socket creation, it removes listener linkage, detaches RDMA ID ownership so caller can destroy it, and releases the socket.

## Concurrency
- Listener `pending` and `ready` lists are guarded by `lsc->listen.lock`.
- Connect request handler assumes RDMA CM callback context may sleep and warns if in interrupt.
