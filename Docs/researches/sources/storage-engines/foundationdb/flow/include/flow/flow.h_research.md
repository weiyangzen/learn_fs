# sources/storage-engines/foundationdb/flow/include/flow/flow.h

## Purpose
Central Flow async runtime header defining core value wrappers, serialization helpers, futures/promises, streams, actor callback state, lineage sampling, and network scheduling wrappers.

## Important APIs, Types, And Functions
Exports include `Void`, `Never`, `ErrorOr<T>`, `CachedSerialization<T>`, `Callback`, `SingleCallback`, `ActorLineage`, `LineageReference`, `LocalLineage`, `SAV<T>`, `Future<T>`, `StrictFuture<T>`, `Promise<T>`, `NotifiedQueue<T>`, `FutureStream<T>`, `PromiseStream<T>`, `Actor`, `ActorCallback`, `ActorSingleCallback`, and wrappers such as `now`, `delay`, `orderedDelay`, `delayUntil`, `delayJittered`, `yield`, and `check_yield`.

## Control Flow
`Promise` and `Future` share `SAV` single-assignment state. Sending a value/error/Never fires callbacks. Last-promise drop before setting sends `broken_promise`; last-future drop can cancel producers. Streams use `NotifiedQueue`. Actor compiler output resumes through callback subclasses.

## State And Persistence Behavior
Runtime async state is in-memory. `CachedSerialization` can cache binary/object encodings using `g_network->protocolVersion()`. Actor lineage is optional sampling/debug state.

## Dependencies And Integration Points
Depends on Arena, Error, random, network, serialization, Swift bridging, coroutines, and generic actors. Nearly all Flow/fdbrpc/fdbclient/fdbserver actor and RPC code depends on it.

## Risks And Edge Cases
Callback rings and reference counts are fragile. `Future::get` throws stored errors. `PromiseStream::getReply` is at-least-once delivery. Cached object serialization has noted limitations for direct ObjectWriter caching.

## Test Signals
Actor cancellation, trivial/networked futures, quorum, broken promises, stream errors/end, `ErrorOr` and cached serialization round trips, Swift continuation tests, and deterministic jittered delays.
