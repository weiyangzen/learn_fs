
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcNoSuchMethodException.java

## Purpose

`RpcNoSuchMethodException` reports that a requested RPC method is not available on the resolved protocol.

## Important APIs, types, and functions

It extends `RpcServerException`, has a public message constructor, returns `RpcStatusProto.ERROR`, and maps to `RpcErrorCodeProto.ERROR_NO_SUCH_METHOD`.

## Control flow

`ProtobufRpcEngine.ProtoBufRpcInvoker` throws this when the generated `BlockingService` descriptor has no method matching the request header.

## State and persistence behavior

Only exception message and inherited stack/cause state are stored.

## Dependencies and integration points

It integrates server dispatch with protobuf RPC response headers and client-side remote exception handling.

## Risks and test signals

Tests should cover unknown method requests, error-code propagation to clients, and distinction from unknown protocol/version errors.
