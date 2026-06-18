
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtobufHelper.java

## Purpose

`ProtobufHelper` provides a small helper for converting protobuf `ServiceException` failures back into Java `IOException`s expected by Hadoop RPC callers.

## Important APIs, types, and functions

`getRemoteException(ServiceException se)` returns the cause if it is an `IOException`; otherwise it wraps the `ServiceException` in a new `IOException`. The constructor is private because the class is static-only.

## Control flow

Client code catches `ServiceException` from protobuf stubs and calls this helper. A null cause or non-IO cause is treated as unexpected and wrapped.

## State and persistence behavior

The helper is stateless and persists nothing.

## Dependencies and integration points

It depends on protobuf `ServiceException` and Java `IOException`. It integrates with client-side translator layers that expose checked IO exceptions instead of protobuf exceptions.

## Risks and test signals

Tests should cover `RemoteException` causes, other `IOException` causes, null causes, and non-IO causes. Preserving the original cause chain is important for retry and failover logic.
