<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/conn.go -->
# sources/user-network-fs/go-nfs/conn.go

## Purpose
Implements ONC RPC-over-TCP request parsing, response framing, handler dispatch, serialized writes, and generic RPC/NFS error handling.

## Important APIs, Types, and Functions
Important types are `conn`, `request`, `response`, `ResponseCode`, `readRequestHeader`, `handle`, `err`, `Write`, `writeHeader`, `drain`, and `finish`.

## Control Flow
A connection reads record-marked RPC frames, decodes the XID/type/header into a limited body reader, dispatches by program/procedure, drains unread request bytes, formats application errors if needed, and enqueues the response buffer to a writer goroutine that prepends the last-fragment marker.

## State and Persistence Behavior
State includes the network connection, per-request response buffer/responded flag/error formatter, and write serializer channel. It does not reconstruct multi-fragment records.

## Dependencies and Integration Points
Depends on go-nfs `Server.handlerFor`, go-nfs-client RPC/XDR packages, TCP record marking, and procedure handlers registered from `nfs.go`/`mount.go`.

## Risks and Edge Cases
Fragment reconstruction is unimplemented; malformed auth/version handling is minimal; error marshalling uses mixed endian in some RPC errors; writer goroutine failure silently returns.

## Test Signals
Protocol tests should cover short records, unsupported procedures, unread body drain, duplicate header writes, multi-request serialization, and client disconnects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/conn.go -->
