
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/IpcException.java

## Purpose

`IpcException` is a simple `IOException` subtype for IPC-layer connection establishment failures.

## Important APIs, types, and functions

It provides a single public constructor accepting an error string and inherits `IOException` behavior.

## Control flow

Callers throw this exception when IPC setup cannot proceed. There is no additional local flow.

## State and persistence behavior

The only state is the inherited exception message and stack trace. Nothing is persisted.

## Dependencies and integration points

It integrates with client/server connection code through Java checked exception handling.

## Risks and test signals

Tests should only need to verify message propagation and catchability as `IOException`. The class does not carry RPC status codes, so wire-level mappings must happen elsewhere.
