# File Research: sources/os/linux/linux/fs/smb/client/smbdirect.c

## Purpose

`smbdirect.c` implements the CIFS client’s SMB Direct transport adapter when `CONFIG_CIFS_SMB_DIRECT` is enabled. It wraps the kernel `linux/smbdirect.h` socket API to create, reconnect, destroy, send, receive, and register memory for RDMA-backed SMB transport.

## Main Responsibilities

- Define default SMB Direct and RDMA tuning parameters exposed as module parameters or globals.
- Configure SMB Direct logging classes and bridge SMB Direct logging into CIFS debug output.
- Create SMB Direct connections using port 5445 first, then port 445 as fallback.
- Set initial socket parameters including credit limits, send/receive sizes, fragmented receive size, FRMR depth, keepalive intervals, and RDMA connection timeouts.
- Reconnect and destroy SMB Direct connections associated with `TCP_Server_Info`.
- Send one or more SMB requests over SMB Direct, fragmenting metadata and payload iterators according to negotiated send size.
- Receive data through the SMB Direct socket into upper-layer message iterators.
- Register/deregister memory regions for RDMA read/write offload and fill SMB2 RDMA buffer descriptors.
- Emit debug/proc output for RDMA transport state.

## Key Control Flow

- `_smbd_get_connection()` allocates `struct smbd_connection`, creates a kernel SMB Direct socket, sets initial parameters and kernel settings, patches the destination port, connects synchronously, and returns the connection.
- `smbd_get_connection()` first tries SMB Direct port 5445, then port 445, then records the negotiated RDMA read/write threshold.
- `smbd_reconnect()` destroys any existing transport and creates a new connection for the server destination address.
- `smbd_send()` computes total payload length across request arrays, rejects payloads exceeding `max_fragmented_send_size`, sends all metadata iovecs and data iterators in a single batch, flushes the batch, and waits for pending sends to drain.
- `smbd_register_mr()` and `smbd_deregister_mr()` wrap lower SMB Direct memory-region APIs used by `smb2pdu.c` read/write offload paths.

## Dependencies and Integration

- Includes `smbdirect.h`, `cifsproto.h`, and `smb2proto.h`.
- Uses the exported SMB Direct namespace via `MODULE_IMPORT_NS("SMBDIRECT")`.
- Depends on `smb_rqst_len()` to compute upper-layer request lengths.
- Integrates with `TCP_Server_Info->smbd_conn`, `server->rdma`, and `server->rdma_readwrite_threshold`.
- Used by SMB2 read/write request construction for RDMA buffer descriptors and by the transport layer for send/receive.

## Risk Notes

- `smbd_send()` mutates request iterators while sending; callers must not assume iterators are reusable afterward without reset.
- Payload size checks depend on negotiated SMB Direct parameters.
- Destination port is written directly into the supplied socket address before connect.
- Connection teardown assumes no upper-layer user remains; lifetime must be coordinated by CIFS server/session management.
