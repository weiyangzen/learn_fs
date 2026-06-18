
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtocolInfo.java

## Purpose

`ProtocolInfo` is a runtime annotation for overriding the default RPC protocol name and optionally declaring protocol version.

## Important APIs, types, and functions

The annotation has `protocolName()` and `protocolVersion()` elements. `protocolVersion()` defaults to `-1`, which tells `RPC.getProtocolVersion()` to fall back to the legacy `versionID` field.

## Control flow

`RPC.getProtocolName()` and `RPC.getProtocolVersion()` inspect this annotation when registering protocols and constructing client request headers.

## State and persistence behavior

Annotation values are class metadata retained at runtime. There is no mutable state or persistence.

## Dependencies and integration points

It integrates protocol interfaces, generated protobuf translators, and `RPC.Server` protocol maps.

## Risks and test signals

Mismatched names or versions break client/server lookup. Tests should cover annotated name override, annotated version override, fallback to `versionID`, and failure when neither annotation version nor `versionID` is available.
