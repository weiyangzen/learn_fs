
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RPC.java

## Purpose

`RPC` is the central utility and abstraction layer for Hadoop IPC protocols. It resolves protocol names and versions, manages protocol-to-engine mapping, creates client proxies, closes proxies, builds servers, and maintains server-side protocol implementation maps.

## Important APIs, types, and functions

`RpcKind` identifies built-in, writable, and protobuf RPC kinds. `RpcInvoker` is the server-side dispatch contract. Static helpers include `getProtocolName()`, `getProtocolVersion()`, `setProtocolEngine()`, `getProtocolProxy()`, `getServerAddress()`, `getConnectionIdForProxy()`, `stopProxy()`, and `getRpcTimeout()`. `VersionMismatch` maps version errors to `ERROR_RPC_VERSION_MISMATCH`.

`Builder` captures server settings and constructs an engine-specific server. `RPC.Server` extends the lower-level IPC `Server`, names servers from implementation classes, stores per-kind protocol maps keyed by protocol name/version, registers implementations, exposes supported versions, sets scheduler priority for configured client principals, and dispatches calls through registered invokers.

## Control flow

Client setup calls `getProtocolProxy()`, initializes SASL if security is enabled, resolves the protocol engine from configuration or the default `ProtobufRpcEngine`, and delegates proxy construction. `stopProxy()` closes either a `Closeable` proxy or a closeable invocation handler.

Server setup uses `Builder.build()` to validate mandatory protocol, instance, and configuration, then asks the configured engine to create a server. During registration, `RPC.Server` resolves protocol name/version, stores implementation metadata in the per-kind map, and optionally marks the configured client principal as highest scheduler priority. Incoming calls route through `call()`, which selects the `RpcInvoker` for the request kind.

## State and persistence behavior

Static state includes the process-wide `PROTOCOL_ENGINES` cache. Each server stores protocol implementation maps in memory. No state is persisted; protocol registration must happen at process startup or server construction.

## Dependencies and integration points

`RPC` ties together `Configuration`, `CommonConfigurationKeys`, `Client.ConnectionId`, retry policies, SASL/security utilities, token secret managers, `ReflectionUtils`, lower-level `Server`, and protobuf error codes. It is the primary API used by Ozone code to configure `ProtobufRpcEngine` and create service endpoints.

## Risks and test signals

Protocol version discovery fails at runtime if neither `ProtocolInfo` version nor `versionID` exists. The engine cache is keyed only by protocol class, so configuration changes after first lookup may not take effect. `stopProxy()` throws for mocks or adapters that do not expose closeable handlers. Tests should cover annotation and `versionID` paths, engine cache behavior, secure-client SASL initialization, builder mandatory fields, server name extraction for generated/anonymous classes, unknown protocol/version dispatch, and translated proxy connection lookup.
