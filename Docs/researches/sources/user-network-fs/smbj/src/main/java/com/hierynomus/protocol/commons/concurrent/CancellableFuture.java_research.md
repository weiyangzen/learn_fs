# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/CancellableFuture.java

## Purpose
Future wrapper that coordinates cancellation with an external callback while delegating blocking get operations to a wrapped AFuture.

## Important APIs / Types / Functions
Defines class `CancellableFuture` in package `com.hierynomus.protocol.commons.concurrent`. Important methods/functions include `CancellableFuture`, `cancel`, `isCancelled`, `isDone`, `get`. Important fields include `wrappedFuture`, `callback`, `cancelled`, `lock`. Source size: 90 lines.

## Control Flow
Control flow centers on Future or Promise state transitions. Callers deliver values or errors, wait with optional timeouts, sequence or transform wrapped futures, and cancellation wrappers invoke external callbacks while delegating result retrieval.

## State and Persistence
State fields observed: wrappedFuture, callback, cancelled, lock. Concurrency state is explicit and lives only in process memory. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.smbj.common.SMBRuntimeException. JDK/JCE dependencies: java.util.concurrent.ExecutionException, java.util.concurrent.TimeUnit, java.util.concurrent.TimeoutException, java.util.concurrent.atomic.AtomicBoolean, java.util.concurrent.locks.ReentrantReadWriteLock.

## Risks and Edge Cases
concurrency semantics need tests for timeout, cancellation, interruption, and double-close paths.

## Test Signals
Cover success, timeout, wrapped error, interrupted wait, cancellation callback, and transformed/sequenced future ordering.
