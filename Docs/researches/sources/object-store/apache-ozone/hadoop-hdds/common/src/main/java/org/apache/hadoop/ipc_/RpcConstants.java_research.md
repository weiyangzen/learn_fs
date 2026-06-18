
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcConstants.java

## Purpose

`RpcConstants` centralizes wire-level constants for Hadoop IPC connections and special call IDs.

## Important APIs, types, and functions

Constants include special call IDs for authorization failure, invalid calls, connection context, and ping; empty dummy client ID; invalid retry count; the `"hrpc"` connection header as a `ByteBuffer`; post-header byte count; and current wire protocol version `9`.

## Control flow

Connection setup and request framing code read these constants while parsing or emitting headers. There is no executable flow in the class.

## State and persistence behavior

All state is static constants. The public `HEADER` buffer is mutable as a `ByteBuffer` object, so consumers should avoid changing its position or contents.

## Dependencies and integration points

It integrates with low-level `Client` and `Server` connection handshakes and protocol compatibility checks.

## Risks and test signals

Wire compatibility depends on these values. Tests should verify header bytes, version negotiation, special call ID handling, retry-count defaults, and that callers duplicate/read-only-wrap `HEADER` before mutating buffer position.
