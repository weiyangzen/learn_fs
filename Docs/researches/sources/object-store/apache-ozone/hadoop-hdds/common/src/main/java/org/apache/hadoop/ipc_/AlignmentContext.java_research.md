# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/AlignmentContext.java

## Purpose
Interface for propagating and validating replicated state alignment information through IPC request and response headers.

## Important APIs, Types, And Functions
Methods are `updateResponseState`, `receiveResponseState`, `updateRequestState`, `receiveRequestState`, `getLastSeenStateId`, and `isCoordinatedCall`.

## Control Flow
Client-side code calls `updateRequestState` before sending and `receiveResponseState` after success. Server-side code calls `receiveRequestState` while handling request headers and `updateResponseState` while building response headers. Implementations decide whether a protocol/method is coordinated and may reject requests via `IOException`.

## State And Persistence
This interface owns no state; implementations maintain last-seen state IDs and any synchronization thresholds.

## Dependencies And Integration Points
Uses IPC protobuf request/response header builders. `Client.Call` stores an optional `AlignmentContext` and updates it on successful responses.

## Risks
Incorrect implementation can allow stale reads or reject valid calls. Method-name/protocol-name classification must match generated RPC names.

## Test Signals
Tests should cover request header population, response state receipt, threshold rejection, and coordinated-call classification in OM/SCM HA paths.
