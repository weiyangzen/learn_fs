# sources/user-network-fs/samba/source4/smb_server/smb_server.c

## Purpose
This file is the connection-level entry point for the source4 SMB service. It accepts stream sockets, configures packet framing, detects SMB1 vs SMB2 on the first request, installs the protocol-specific receive callback, manages socket send/receive events, and creates listening sockets for configured SMB transports.

## Important APIs, Types, And Functions
The exported function is `smbsrv_add_socket`. Internal functions include `smbsrv_recv_generic_request`, `smbsrv_terminate_connection`, event handlers `smbsrv_recv` and `smbsrv_send`, `smbsrv_recv_error`, and `smbsrv_accept`. It uses `stream_server_ops smb_stream_ops` to bind accept/recv/send behavior.

## Control Flow
On accept, the code allocates `smbsrv_connection`, initializes a packet context with NBT full-request detection and serialized output, stores loadparm and stream connection pointers, initializes management, registers the `smb_server` IRPC name, and obtains the share context. The first packet is inspected: nonzero NBT marker or SMB magic selects SMB1, SMB2 magic selects SMB2 if the configured max protocol permits it, and invalid packets terminate the stream. `smbsrv_add_socket` parses configured SMB transports, ignores unsupported QUIC/unknown entries, and calls `stream_setup_socket` for NBT/TCP ports.

## State And Persistence
The file initializes per-connection state: packet context, share context, connection statistics, loadparm reference, and protocol-specific callbacks. It does not persist disk data.

## Dependencies And Integration Points
It integrates service_stream, service_task, packet transport, SMB1 and SMB2 initialization paths, loadparm transport configuration, share configuration, messaging/IRPC, and network socket setup. Downstream protocol handlers live in `smb/` and `smb2/`.

## Risks And Test Signals
Risks include first-packet protocol confusion, max-protocol gating for SMB2, transport parsing that silently ignores unsupported entries, share context initialization failure terminating accepted sockets, and packet serialization limiting concurrency on a connection. Tests should cover SMB1 first packets, SMB2 first packets, invalid magic, special NBT session packets, disabled SMB2 max protocol, multiple configured transports, and share-init failure handling.
