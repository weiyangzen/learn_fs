# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/SecretKeyProtocolClientSideTranslatorPB.java

## Purpose

This translator adapts `SecretKeyProtocol` and `SecretKeyProtocolScm` calls to the generated SCM secret-key protobuf service with failover/retry support.

## Important APIs, Types, and Functions

The constructor creates a retrying `BlockingInterface` proxy from `SecretKeyProtocolFailoverProxyProvider`. `submitRequest(Type, Consumer<Builder>)` adds command type and trace ID. Methods include `getCurrentSecretKey`, `getSecretKey(UUID)`, `getAllSecretKeys`, and `checkAndRotate(boolean)`.

## Control Flow

Methods build nested request protos where needed, submit a wrapper RPC, validate status via `handleError`, and convert protobuf keys with `ManagedSecretKey.fromProtobuf`. Missing `getSecretKey` response returns `null`.

## State and Persistence Behavior

Only the PB proxy is stored. Key state and persistence live in SCM.

## Dependencies and Integration Points

It integrates secret-key failover proxy providers, tracing, generated `SCMSecretKeyProtocolProtos`, and `SCMSecretKeyException`.

## Risks and Test Signals

The class implements SCM rotation even when used through non-SCM roles, relying on proxy/interface selection and server authorization. Tests should cover UUID bit conversion, missing key null return, all-key list conversion, status error mapping, trace propagation, and close behavior.
