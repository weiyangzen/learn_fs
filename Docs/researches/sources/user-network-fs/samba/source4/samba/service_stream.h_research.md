<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_stream.h -->
# sources/user-network-fs/samba/source4/samba/service_stream.h

## Purpose

This header defines the public stream-service structures and callback contract for source4 stream servers.

## Important APIs, Types, and Functions

`struct stream_connection` contains stream ops, process model ops, server ID, private data, tevent fd/context, socket or tstream, imessaging context, loadparm context, local/remote addresses, optional session info, processing/termination flags, and model process context. `struct stream_server_ops` provides `name`, `accept_connection`, `recv_handler`, and `send_handler`. It declares `stream_terminate_connection()`.

## Control Flow

The header has no executable flow, but its fields are filled by `service_stream.c` and consumed by protocol-specific stream services and named-pipe adapters.

## State and Persistence Behavior

`stream_connection` is the in-memory per-connection state container. The `processing` and `terminate` fields coordinate deferred shutdown during callbacks.

## Dependencies and Integration Points

It depends on generated `server_id` definitions and forward-visible Samba types such as model ops, sockets, tstream, tsocket addresses, imessaging, loadparm, and auth session info.

## Risks and Edge Cases

Consumers must treat ownership as talloc-managed and avoid freeing embedded resources out from under `stream_terminate_connection()`. Callbacks must be prepared for `socket` to be `NULL` on merged or tstream-taken connections.

## Test Signals

Compile coverage for stream services validates structure visibility. Runtime tests should exercise recv/send callbacks, deferred termination, and named-pipe handoff that changes `ops` and `private_data`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_stream.h -->
