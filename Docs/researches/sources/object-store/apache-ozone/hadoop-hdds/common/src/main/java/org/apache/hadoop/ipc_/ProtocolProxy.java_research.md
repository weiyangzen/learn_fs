
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtocolProxy.java

## Purpose

`ProtocolProxy<T>` is a lightweight holder for a client-side proxy object associated with a protocol interface.

## Important APIs, types, and functions

The constructor stores `protocol` and `proxy`; `getProxy()` returns the proxy. The stored protocol field is not otherwise used in this class.

## Control flow

RPC engines return `ProtocolProxy` from `getProxy()`. Callers unwrap it to obtain the dynamic proxy or translator.

## State and persistence behavior

State is just the protocol class reference and proxy instance. Nothing is persisted.

## Dependencies and integration points

It is returned by `RpcEngine.getProxy()` and `RPC.getProtocolProxy()`, and consumed by client setup code.

## Risks and test signals

The class does not validate that the proxy implements the protocol. Tests should cover generic typing, null handling expectations, and downstream `RPC.stopProxy()` behavior on the contained proxy.
