
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtobufRpcEngine.java

## Purpose

`ProtobufRpcEngine` is the RPC engine for protobuf-based Hadoop protocols. It builds client-side dynamic proxies, serializes protobuf request headers and payloads, creates protobuf RPC servers, and dispatches server-side calls through generated `BlockingService` descriptors.

## Important APIs, types, and functions

The static initializer registers `RPC_PROTOCOL_BUFFER` with `Server.registerProtocolEngine()` and the `RpcProtobufRequest` deserializer. `getProxy()` returns a `ProtocolProxy` backed by an `Invoker`. `getServer()` returns a protobuf-aware `Server`.

`Invoker` implements `RpcInvocationHandler`: it builds request headers, validates protobuf method arguments, calls `Client.call()`, caches return prototypes by method name, deserializes response buffers, exposes `getConnectionId()`, and closes cached clients. `Server` extends `RPC.Server`, registers the protocol implementation, and owns `ProtoBufRpcInvoker`. `RpcProtobufRequest` stores a lazily decoded request header and optional protobuf payload.

## Control flow

Client calls hit the dynamic proxy. The `Invoker` expects exactly two arguments, an RPC controller and protobuf `Message`; it creates `RequestHeaderProto`, wraps header/payload in `RpcProtobufRequest`, sends it through the shared `ClientCache`, and decodes the returned `RpcWritable.Buffer` using the method return type's `getDefaultInstance()`.

On the server, `ProtoBufRpcInvoker.call()` reads the protobuf request header, resolves protocol name and client version against `RPC.Server`'s protocol map, looks up the generated method descriptor, decodes the payload using the service request prototype, initializes detailed metrics, sets thread-local call info, invokes `callBlockingMethod()`, and wraps the result as `RpcWritable`. `ServiceException` causes and other exceptions update detailed metrics before propagating.

## State and persistence behavior

Client state includes a static `ClientCache`, per-proxy `ConnectionId`, cached return protobuf prototypes, fallback auth flag, and optional alignment context. Server state is inherited from `RPC.Server` protocol maps plus a thread-local current call info. No durable state is stored.

## Dependencies and integration points

This file integrates protobuf `Message`, `BlockingService`, and descriptors with Hadoop `Client`, `Server`, `RPC`, `RpcWritable`, `RequestHeaderProto`, `AlignmentContext`, `UserGroupInformation`, `RetryPolicy`, and token secret managers. Many Ozone server/client utilities set protocol engines to `ProtobufRpcEngine`.

## Risks and test signals

Method argument shape, return type reflection, and descriptor lookup are brittle compatibility points for generated protobuf stubs. Static `ClientCache` sharing requires correct `close()`/`stopProxy()` behavior. Tests should cover unknown protocol, version mismatch, unknown method, null parameters, remote `ServiceException` propagation, fallback-to-simple-auth mutation, alignment context propagation, client cache shutdown, and protocol registration through `RPC.Builder`.
