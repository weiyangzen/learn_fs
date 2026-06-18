# File Research: sources/os/linux/linux-stable/fs/smb/server/transport_rdma.c

## Summary
Implements the ksmbd SMB Direct server transport adapter using the shared kernel `smbdirect_socket` API. It listens on RDMA-capable SMB Direct ports, accepts RDMA connections, creates ksmbd connection threads, and exposes SMB Direct read/write/RDMA operations through `ksmbd_transport_ops`.

## Main Responsibilities
- Define SMB Direct listener defaults: ports, negotiate timeout, keepalive interval/timeout, RDMA read/write depth, credits, and message sizes.
- Clamp user-configured maximum RDMA read/write I/O size.
- Create two listeners: port 445 for InfiniBand/RoCE and port 5445 for iWARP.
- Configure `smbdirect_socket_parameters`, kernel polling, and logging callbacks.
- Accept SMB Direct sockets in listener kthreads and start per-connection `ksmbd_conn_handler_loop` threads.
- Wrap receive, send iterator, RDMA read, RDMA write, shutdown, disconnect, and free operations.
- Check net devices for RDMA capability via the common smbdirect layer.

## Key Interfaces
`ksmbd_rdma_init()`, `ksmbd_rdma_stop_listening()`, `ksmbd_rdma_capable_netdev()`, `init_smbd_max_io_size()`, and `get_smbd_max_read_write_size()`.

## Important Behavior
Accepted RDMA sockets are wrapped in `struct smb_direct_transport`, associated with a newly allocated `ksmbd_conn`, inserted into the global connection hash, and dispatched to the common ksmbd connection handler. Transport operations delegate wire movement to `smbdirect_connection_recvmsg()`, `smbdirect_connection_send_iter()`, and `smbdirect_connection_rdma_xmit()`.

## Cross-File Interactions
Called from server startup/shutdown and configured by IPC startup. SMB2 read/write paths can use `kt->ops->rdma_read` and `rdma_write`. The header provides stubs when SMB Direct server support is disabled.

## Risks
Listener lifetime, socket shutdown, and connection-thread startup must be ordered carefully to avoid leaked sockets or use-after-free. Negotiated RDMA sizes and credits must stay compatible with SMB Direct protocol constraints and the shared smbdirect implementation.
