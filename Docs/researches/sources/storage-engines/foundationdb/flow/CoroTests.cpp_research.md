# sources/storage-engines/foundationdb/flow/CoroTests.cpp

## Purpose
`CoroTests.cpp` is a broad unit and performance test suite for Flow's C++ coroutine integration: futures, streams, cancellation, choose/race combinators, async maps, async results, generators, mutexes, uncancellable actors, and no-throw-on-cancel semantics.

## Important APIs, Types, and Functions
The file defines many small coroutine helpers such as `oneWaitActor`, `chooseTwoActor`, `consumeOneActor`, `sumActor`, `coro::errorOr` use cases, `YieldMockNetwork`, `YAMRandom`, `Tracker`, `LifetimeTracked`, AsyncResult producers, generator helpers, file line readers, and no-throw-on-cancel recorders. Test cases cover `yieldedFuture`, `Choose`, `race`, `quorum`, `getAll`, `FlowMutex`, `PromiseStream`, `StrictFuture`, `AsyncGenerator`, and `Generator`.

## Control Flow
Tests create ready, delayed, failing, cancelled, and dropped futures and assert exact readiness, reference counts, error codes, move/copy counts, cancellation propagation, and result ordering. Some tests use `YieldMockNetwork` to force `yield` scheduling behavior one tick at a time. Generator tests write a randomized 1MB file, read it back line-by-line using block generators, and compare expected arena-backed lines.

## State and Persistence Behavior
Most state is transient in promises, futures, coroutine frames, streams, and local counters. `testReadLines` creates and deletes a temporary file through `IAsyncFileSystem` when available. `LifetimeTracked` static count detects leaked coroutine result state. Several tests inspect promise/future reference counts after cancellation or completion.

## Dependencies and Integration Points
The file depends on Flow unit tests, async file APIs, network/yield behavior, tracing, TLS config, fmt, standard coroutines-adjacent utilities, and deterministic randomness. It is linked into Flow tests through `forceLinkCoroTests`.

## Risks and Edge Cases
The suite intentionally codifies subtle semantics: first-ready tie-breaking for `race`, cancellation after `Choose` is already ready, `NoThrowOnCancel` bypassing catch blocks on cancellation but not on ordinary errors, queued versus callback-delivered stream moves, and cancellation of remaining producers on `quorum`/`getAll` completion or error. Performance tests with one million iterations can be expensive and are partly diagnostic.

## Test Signals
Every `TEST_CASE` is a signal. Notable names include `/flow/coro/cancel1`, `/flow/coro/trivial_actors`, `/flow/coro/YieldedAsyncMap/randomized`, `/flow/coro/AsyncResult/noThrowOnCancel`, `/flow/coro/FlowMutex`, `/flow/coro/generators`, `/flow/coro/actor`, `/flow/coro/noThrowOnCancel/*`, and `/flow/coro/race*`.
