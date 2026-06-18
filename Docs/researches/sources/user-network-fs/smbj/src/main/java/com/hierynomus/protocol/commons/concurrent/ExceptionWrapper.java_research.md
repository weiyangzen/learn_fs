# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/ExceptionWrapper.java

## Purpose
Small concurrency utility in the protocol commons layer. ExceptionWrapper adapts Java Future/lock patterns into the project AFuture, promise, sequencing, transformation, or exception-wrapping model.

## Important APIs / Types / Functions
Defines interface `ExceptionWrapper` in package `com.hierynomus.protocol.commons.concurrent`. Source size: 21 lines.

## Control Flow
Control flow centers on Future or Promise state transitions. Callers deliver values or errors, wait with optional timeouts, sequence or transform wrapped futures, and cancellation wrappers invoke external callbacks while delegating result retrieval.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Cover success, timeout, wrapped error, interrupted wait, cancellation callback, and transformed/sequenced future ordering.
