# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/MultiVersionAssignmentVars.h

## Purpose
Provides `ThreadSingleAssignmentVar` adapters used by the multiversion client layer to bridge external C API futures into FoundationDB `ThreadFuture`s and to compose/cancel those futures safely across callbacks, abort signals, and mapped operations.

## Important APIs, Types, And Functions
`AbortableSingleAssignmentVar<T>` wraps a source `ThreadFuture<T>` and an abort signal, returning the source result unless the abort signal wins, in which case it returns `cluster_version_changed()`. `abortableFuture()` constructs it. `DLThreadSingleAssignmentVar<T>` wraps an externally loaded `FdbCApi::FDBFuture` and an extractor function, translating C API completion into a `ThreadFuture<T>`. `toThreadFuture()` constructs it. `MapSingleAssignmentVar<S,T>` and `mapThreadFuture()` map `ErrorOr<S>` to `ErrorOr<T>`. `FlatMapSingleAssignmentVar<S,T>` and `flatMapThreadFuture()` map to a second `ThreadFuture<T>` and forward its result.

## Control Flow
Each adapter registers itself as a callback, increments assignment-var references while callbacks are outstanding, and sends a value or error when fired. Cancellation clears callbacks where possible, cancels underlying futures, releases retained memory, and sends `operation_cancelled()` when no completion signal won. `DLThreadSingleAssignmentVar` may dispatch callback application onto the main thread depending on `MultiVersionApi::callbackOnMainThread`.

## State And Persistence Behavior
There is no durable state. Runtime state includes source futures, abort signals, C API future pointers, extractor functions, refcounts, spin locks, cancellation/release flags, and mapped futures. Memory release is explicit through `cleanupUnsafe()` to avoid holding large future payloads.

## Dependencies And Integration Points
The header depends on `MultiVersionTransaction.h` for `FdbCApi` and `MultiVersionApi`, and on Flow thread helper primitives. It is used by dynamically loaded and multiversion client implementations to adapt callback-based C futures into FDB's thread future abstraction.

## Risks And Test Signals
Risks include callback/refcount races, double-destroying external futures, failing to cancel mapped futures, sending two results, and main-thread callback ordering differences. Test signals should include ready-before-registration futures, cancellation before and after completion, abort-vs-source races, error mapping, flat-map cancellation/release paths, and external future destruction under concurrent callbacks.
