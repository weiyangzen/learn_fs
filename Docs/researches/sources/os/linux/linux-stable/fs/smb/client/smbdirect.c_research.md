# File Research: sources/os/linux/linux-stable/fs/smb/client/smbdirect.c

## Summary
Implements the CIFS SMB Direct transport adapter for RDMA-enabled SMB connections. In this version it delegates most low-level RDMA connection, send/receive, memory registration, and debug display mechanics to the kernel `smbdirect` socket API while preserving CIFS module parameters, logging classes, connection lifecycle, and upper-layer send/receive wrappers.

## Main Responsibilities
- Define SMB Direct default tunables for credits, send/receive sizes, fragmented receive size, keepalive interval, FRMR depth, and RDMA read/write threshold.
- Expose module parameters for SMB Direct logging class and level.
- Bridge CIFS logging requests to `smbdirect_socket` logging callbacks.
- Create SMB Direct connections on port 5445 first and then fall back to port 445 with port-family constraints for iWARP versus InfiniBand/RoCE behavior.
- Configure initial `smbdirect_socket_parameters`, kernel polling settings, connect timeouts, keepalive timeouts, and RDMA resource counts.
- Destroy and reconnect SMB Direct sessions for `TCP_Server_Info`.
- Send CIFS SMB request arrays as SMB Direct payloads, including metadata iovecs and optional data iterators.
- Receive data from the SMB Direct reassembly queue into caller-provided message iterators.
- Register, describe, and deregister memory regions for SMB Direct RDMA read/write offload.
- Emit SMB Direct debug information into CIFS proc/debug output.

## Key Interfaces
- Connection lifecycle: `smbd_get_connection()`, `smbd_reconnect()`, `smbd_destroy()`, and internal `_smbd_get_connection()`.
- Transport I/O: `smbd_send()` and `smbd_recv()`.
- RDMA memory registration: `smbd_register_mr()`, `smbd_mr_fill_buffer_descriptor()`, and `smbd_deregister_mr()`.
- Parameter/debug helpers: `smbd_get_parameters()` and `smbd_debug_proc_show()`.

## Control Flow And Behavior
Connection creation builds an initial parameter block, creates a kernel SMB Direct socket in the CIFS network namespace, installs logging hooks, configures transport parameters and kernel settings, writes the requested port into the destination address, and attempts a synchronous RDMA connect. `smbd_get_connection()` first tries the dedicated SMB Direct port and then ordinary SMB port; after success it clamps the server RDMA read/write threshold to the negotiated maximum fragmented send size.

`smbd_send()` computes the total SMB request length across all request fragments, validates it against the negotiated fragmented send maximum, initializes a send batch, posts each request's metadata kvecs and then its data iterator in chunks that respect the negotiated send size, flushes the batch, waits for pending sends to drain, and returns retryable errors when completion waiting fails.

Memory registration wrappers verify connection state and then call the SMB Direct socket API. These are used by `smb2pdu.c` read/write paths to expose client memory to the server through SMB2 RDMA channel descriptors.

## State And Synchronization
The CIFS-visible state is mainly `server->smbd_conn`, `server->rdma`, and `server->rdma_readwrite_threshold`; deeper queue pair, credit, receive reassembly, and memory registration state is owned by the `smbdirect_socket` layer. Destruction releases the socket before freeing the CIFS wrapper.

## Cross-File Interactions
`connect.c` creates or reconnects SMB Direct sessions when RDMA transport is requested. `smb2pdu.c` uses memory-registration helpers for RDMA offloaded reads and writes. `smbdirect.h` provides stubs when `CONFIG_CIFS_SMB_DIRECT` is disabled.

## Risks
The main risks are negotiated size mismatches, send iterator consumption across multi-fragment requests, connection-state races around reconnect/destroy, and memory-registration lifetime. Because much of the implementation delegates to `linux/smbdirect.h`, CIFS must keep its wrapper assumptions synchronized with the lower-level socket API behavior and negotiated parameter semantics.
