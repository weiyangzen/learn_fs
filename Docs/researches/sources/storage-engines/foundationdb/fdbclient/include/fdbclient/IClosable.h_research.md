# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/IClosable.h

## Purpose
Defines a tiny asynchronous lifecycle interface for disk-backed data structures that can surface internal errors, shut down, or be permanently deleted.

## Important APIs, Types, And Functions
`IClosable` exposes four pure virtual methods. `getError()` returns a future that throws if an internal error occurs and is documented not to be set synchronously inside another API call. `onClosed()` becomes ready when shutdown after `dispose()` or `close()` is complete, but must be obtained before closing. `dispose()` permanently deletes backing data and invalidates the interface. `close()` invalidates the interface without deleting data, with outstanding operations allowed to complete or be abandoned depending on implementation.

## Control Flow
Users typically hold an implementation, start work, monitor `getError()`, optionally acquire `onClosed()`, then call either `close()` for shutdown or `dispose()` for deletion. Implementations decide how to drain or cancel outstanding asynchronous work.

## State And Persistence Behavior
The base interface has no data members. Persistence semantics are delegated: `dispose()` must remove durable backing data, while `close()` must preserve it. Error and closed futures model implementation state transitions.

## Dependencies And Integration Points
Only Flow futures are required. The interface is intended to be mixed into disk-backed components elsewhere in FoundationDB where lifecycle management and background actor error propagation are needed.

## Risks And Test Signals
Risks are mostly contract violations: setting `getError()` reentrantly, allowing `onClosed()` calls after invalidation, deleting data on `close()`, or leaking background operations after `dispose()`. Test signals should assert lifecycle ordering, persistence after close, deletion after dispose, and error propagation from background actors.
