
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtobufRpcEngineCallback.java

## Purpose

`ProtobufRpcEngineCallback` is a callback contract for asynchronous protobuf RPC paths. It receives either a protobuf response message or an error.

## Important APIs, types, and functions

`setResponse(Message message)` supplies the successful response. `error(Throwable t)` reports failure.

## Control flow

The interface itself has no flow. Implementations are expected to be called by asynchronous RPC machinery once a server method completes or fails.

## State and persistence behavior

The interface owns no state. Implementations decide how to store or signal completion.

## Dependencies and integration points

It depends on protobuf `Message` and is part of the protobuf RPC engine surface.

## Risks and test signals

Implementations must define single-completion behavior and thread-safety. Tests should verify success/error exclusivity, null handling expectations, and callback invocation on exceptional server paths.
