# File Research: sources/os/linux/linux/fs/smb/server/transport_rdma.c

Implements ksmbd’s SMBDirect/RDMA transport adapter on top of the shared `smbdirect_socket` infrastructure.

Key behaviors:
- Defines SMBDirect listener ports: 445 for InfiniBand/RoCE and 5445 for iWARP.
- Sets SMBDirect negotiation timeout, keepalive timings, initiator depth, send/receive credits, max send/receive sizes, fragmented receive size, and max read/write size.
- Clamps configured SMBDirect max I/O size to `SMBD_MIN_IOSIZE..SMBD_MAX_IOSIZE`.
- Allocates `ksmbd_transport` instances with ksmbd connections and inserts them into the global connection hash.
- Implements transport ops for read, writev, RDMA read, RDMA write, disconnect, shutdown, and free.
- Creates kernel SMBDirect sockets, sets initial parameters and kernel polling settings, binds/listens on the RDMA ports, and starts listener kthreads.
- Accepts SMBDirect connections and starts per-connection ksmbd handler kthreads.
- Stops and releases RDMA listeners on shutdown.
- Detects RDMA-capable netdevices using common SMBDirect node-type probing.
- Bridges SMBDirect logging into ksmbd debug/error logging.

Dependencies:
- Requires `CONFIG_SMB_SERVER_SMBDIRECT` through the header and imports namespace `SMBDIRECT`.
- Uses connection allocation/free and `ksmbd_conn_handler_loop`.

Role in subsystem:
- Optional high-performance transport layer for SMB3 over RDMA, sharing the same ksmbd connection/request engine as TCP.
