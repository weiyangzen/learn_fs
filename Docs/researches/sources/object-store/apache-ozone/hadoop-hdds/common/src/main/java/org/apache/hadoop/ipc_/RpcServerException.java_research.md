
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcServerException.java

## Purpose

`RpcServerException` is the base class for server-side RPC errors that can be mapped into protobuf response status and error codes.

## Important APIs, types, and functions

It extends `RpcException`, provides public message and message-with-cause constructors, returns `RpcStatusProto.ERROR`, and defaults to `RpcErrorCodeProto.ERROR_RPC_SERVER`.

## Control flow

Server dispatch and validation paths throw this class or subclasses. Response encoding reads `getRpcStatusProto()` and `getRpcErrorCodeProto()` to populate headers.

## State and persistence behavior

Only inherited exception state is stored.

## Dependencies and integration points

It integrates with protobuf `RpcResponseHeaderProto` status/error code fields and the server exception hierarchy.

## Risks and test signals

Subclasses must override error codes when clients need specific retry/failover behavior. Tests should cover default status/code and subclass overrides for no-such-method, no-such-protocol, and version mismatch.
