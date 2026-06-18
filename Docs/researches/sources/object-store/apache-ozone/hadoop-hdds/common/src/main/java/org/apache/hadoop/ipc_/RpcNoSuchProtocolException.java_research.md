
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcNoSuchProtocolException.java

## Purpose

`RpcNoSuchProtocolException` reports that a server does not know the requested RPC protocol.

## Important APIs, types, and functions

It extends `RpcServerException`, has a public message constructor, returns `RpcStatusProto.ERROR`, and maps to `RpcErrorCodeProto.ERROR_NO_SUCH_PROTOCOL`.

## Control flow

Server dispatch throws this when no registered protocol matches the requested protocol name. Ozone HA/failover tests assert this error appears in follower-read failure paths.

## State and persistence behavior

Only inherited exception state is stored.

## Dependencies and integration points

It integrates `RPC.Server`/`ProtobufRpcEngine` protocol lookup with protobuf error codes and remote exception unwrapping.

## Risks and test signals

Tests should cover unknown protocol lookup, error-code propagation, failover handling, and distinction from version mismatch where the protocol exists but the requested version does not.
