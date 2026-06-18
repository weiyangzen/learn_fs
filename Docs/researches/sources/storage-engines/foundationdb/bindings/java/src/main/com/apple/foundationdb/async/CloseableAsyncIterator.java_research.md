# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/CloseableAsyncIterator.java

## Purpose
`CloseableAsyncIterator` combines `AsyncIterator` with `AutoCloseable` for asynchronous streams that own resources and must be closed after use.

## Important APIs, Types, And Functions
It overrides `close()` and provides a default `cancel()` implementation that calls `close()`.

## Control Flow
Consumers can call either `close` or `cancel` to stop work and release resources. `LocalityUtil.BoundaryIterator` implements it for boundary-key scans.

## State And Persistence Behavior
The interface stores no state. Implementations typically own transactions, native futures, file handles, or other closeable resources.

## Dependencies And Integration Points
It extends `AutoCloseable` and `AsyncIterator` and is wrapped by `AsyncUtil.mapIterator(CloseableAsyncIterator, Function)`.

## Risks And Edge Cases
Because `cancel` aliases `close`, implementations should make close idempotent and safe after partial iteration. Users must remember to close these iterators; otherwise resources may leak until finalization or transaction cleanup.

## Test Signals
Tests should cover close idempotence, cancel alias behavior, mapped closeable iterator forwarding, and resource release after early termination.
