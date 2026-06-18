
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcEngine.java

## Purpose

`RpcEngine` defines the pluggable transport/serialization engine contract used by `RPC`.

## Important APIs, types, and functions

`getProxy()` constructs a client-side protocol proxy for a remote address with security, retry, timeout, fallback-auth, and alignment context inputs. `getServer()` constructs an `RPC.Server` for a protocol implementation with bind, handler, reader, queue, secret manager, port-range, and alignment settings.

## Control flow

`RPC.getProtocolProxy()` resolves an engine and delegates client proxy construction. `RPC.Builder.build()` delegates server construction. Implementations such as `ProtobufRpcEngine` supply the concrete serialization and dispatch behavior.

## State and persistence behavior

The interface owns no state. Engine implementations may cache clients or reflection metadata, but this file does not prescribe persistence.

## Dependencies and integration points

It connects `Configuration`, socket factories, retry policies, UGI, token secret managers, `AlignmentContext`, and `RPC.Server`.

## Risks and test signals

Engine implementations must honor the full parameter surface, especially security and alignment context. Tests should use a fake or protobuf engine to verify `RPC` passes all builder/proxy parameters correctly.
