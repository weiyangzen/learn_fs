<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_in_connection.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_in_connection.c

## Purpose

This file implements the inbound WINS Replication TCP server connection layer. It accepts port 42 connections, converts sockets to tstream contexts, reads length-prefixed WREPL PDUs, dispatches decoded calls, writes replies through a queue, supports stream handoff/merge, and binds listening sockets.

## Important APIs, Types, and Functions

- `wreplsrv_terminate_in_connection()` terminates a stream connection with a reason.
- `wreplsrv_process()` decodes a `wrepl_packet`, calls `wreplsrv_in_call()`, and encodes a reply.
- `wreplsrv_accept()` initializes a new inbound connection.
- `wreplsrv_call_loop()` receives one PDU, processes it, queues any reply, and schedules the next read.
- `wreplsrv_call_writev_done()` handles queued write completion and terminate-after-send behavior.
- `wreplsrv_in_connection_merge()` turns an existing outbound stream into an inbound server connection.
- `wreplsrv_setup_sockets()` binds WREPL server sockets on IPv4 interfaces or `0.0.0.0`.

## Control Flow

On accept, the code creates `wreplsrv_in_connection`, a send queue, removes the old file descriptor event, wraps the existing socket in `tstream`, marks the socket no-close, validates IPv4 peer address, resolves the partner, registers an IRPC name, and starts `tstream_read_pdu_blob_send()` with a 4-byte length header. Each completed read creates a call, strips the length header, dispatches the call, writes a reply if one exists, and schedules the next read unless the stream was handed off. Write completion frees the call or terminates when requested.

`wreplsrv_in_connection_merge()` performs similar setup for a stream split from an outbound client connection, preserving peer association context. Socket setup binds per configured IPv4 interface when bind-interfaces-only is set, otherwise all IPv4 addresses.

## State and Persistence Behavior

This file owns transient connection, queue, tstream, and call state. It does not persist WINS data directly; persistence is delegated to call handlers. Stream ownership can move between inbound and outbound roles during WREPL update flows.

## Dependencies and Integration Points

It depends on Samba stream server APIs, socket/tstream helpers, process model, IRPC naming, WREPL NDR encoding, network interface helpers, and `wreplsrv_in_call()`. It integrates with service startup through `wreplsrv_setup_sockets()`.

## Risks and Edge Cases

Only IPv4 peers are accepted. Invalid packets are silently ignored to match Windows behavior. Raw stream callbacks `recv_handler` and `send_handler` should never trigger after tstream conversion; if they do, the connection is terminated. Handoff paths must ensure no further reads/writes use a donated stream.

## Test Signals

Signals include successful socket binding, accepted IPv4 partner connections, correct decode/encode of length-prefixed WREPL PDUs, stable read loop after replies, ignored invalid packets, terminate-after-send stop association, and successful merge of update-triggered streams.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_in_connection.c -->
