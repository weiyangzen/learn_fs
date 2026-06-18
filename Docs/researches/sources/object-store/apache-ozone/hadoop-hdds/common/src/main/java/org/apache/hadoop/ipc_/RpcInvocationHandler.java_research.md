
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcInvocationHandler.java

## Purpose

`RpcInvocationHandler` is the common interface for dynamic proxy handlers used by RPC clients.

## Important APIs, types, and functions

It extends `InvocationHandler` and `Closeable`, and adds `getConnectionId()` to expose the associated `Client.ConnectionId`.

## Control flow

`ProtobufRpcEngine.Invoker` implements this interface. `RPC.getConnectionIdForProxy()` and `RPC.stopProxy()` use it to inspect and close proxies.

## State and persistence behavior

The interface has no state; implementations hold connection/client state.

## Dependencies and integration points

It integrates Java dynamic proxies with Hadoop `Client.ConnectionId` and lifecycle management.

## Risks and test signals

Handlers must be closeable and idempotent enough for `stopProxy()`. Tests should cover connection ID access, close propagation, and translated proxies that unwrap to a handler-backed object.
