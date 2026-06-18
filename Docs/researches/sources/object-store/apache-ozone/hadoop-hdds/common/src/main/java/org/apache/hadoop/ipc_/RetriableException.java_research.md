
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RetriableException.java

## Purpose

`RetriableException` signals that a server could not process a request temporarily and the client may retry.

## Important APIs, types, and functions

It extends `IOException` and provides constructors for wrapping an `Exception` or carrying a message string.

## Control flow

Server code throws this when startup, leadership, or another transient condition prevents processing. Client retry/failover layers inspect the exception type or remote wrapping.

## State and persistence behavior

State is inherited exception message/cause/stack trace only.

## Dependencies and integration points

It integrates with Hadoop/Ozone retry policies and remote exception propagation.

## Risks and test signals

Tests should verify retry classification through direct and `RemoteException`-wrapped paths. Overuse can mask permanent failures, so callers should only throw it for genuinely transient states.
