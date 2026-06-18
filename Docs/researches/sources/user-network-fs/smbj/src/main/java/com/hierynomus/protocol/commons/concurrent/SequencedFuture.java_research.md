# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/SequencedFuture.java

## Purpose
Small concurrency utility in the protocol commons layer. SequencedFuture adapts Java Future/lock patterns into the project AFuture, promise, sequencing, transformation, or exception-wrapping model.

## Important APIs / Types / Functions
Defines class `SequencedFuture` in package `com.hierynomus.protocol.commons.concurrent`. Important methods/functions include `SequencedFuture`, `isCancelled`, `cancel`, `isDone`, `get`. Important fields include `futures`. Source size: 81 lines.

## Control Flow
Control flow centers on Future or Promise state transitions. Callers deliver values or errors, wait with optional timeouts, sequence or transform wrapped futures, and cancellation wrappers invoke external callbacks while delegating result retrieval.

## State and Persistence
State fields observed: futures. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.util.ArrayList, java.util.List, java.util.concurrent.ExecutionException, java.util.concurrent.Future, java.util.concurrent.TimeUnit, java.util.concurrent.TimeoutException.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Cover success, timeout, wrapped error, interrupted wait, cancellation callback, and transformed/sequenced future ordering.
