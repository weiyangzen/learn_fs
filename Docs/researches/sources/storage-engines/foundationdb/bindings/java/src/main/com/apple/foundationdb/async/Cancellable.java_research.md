# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/Cancellable.java

## Purpose
`Cancellable` is a small contract for operations or signals whose outstanding work can be cancelled.

## Important APIs, Types, And Functions
It defines one method, `cancel()`, documented as non-blocking, idempotent, and non-throwing for non-fatal conditions.

## Control Flow
Implementations are expected to stop work and notify all consumers that no result will be returned. `AsyncIterator` uses the same cancellation shape directly rather than extending this interface.

## State And Persistence Behavior
The interface stores no state. Implementations typically maintain cancellation flags and cancel outstanding futures.

## Dependencies And Integration Points
It belongs to the async support package and documents a cancellation model shared conceptually by range iterators and closeable async iterators.

## Risks And Edge Cases
The interface cannot enforce idempotence or non-throwing behavior. Shared operations should define whether one consumer cancellation cancels all consumers.

## Test Signals
Tests for implementations should verify repeated cancel calls, cancellation before and after completion, and downstream consumer notification.
