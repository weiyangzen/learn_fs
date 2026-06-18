# sources/storage-engines/foundationdb/fdbrpc/FlowTests.actor.cpp

## Purpose
`FlowTests.actor.cpp` is a broad unit/performance test suite for Flow actor compiler behavior, futures, promises, streams, cancellation, yielded futures, async maps, deterministic randomness, mutexes, thread-return streams, and fdbrpc `waitValueOrSignal` disconnect/retry behavior.

## Important APIs, Types, and Functions
The file defines many small actor helpers (`emptyActor`, `oneWaitActor`, `chooseTwoActor`, `sumActor`, `testCancelled`, `waitAfterCancel`, `mutexTest`, etc.), callback helper templates (`LambdaCallback`, `onReady` overloads), `YieldMockNetwork`, `YAMRandom`, serializable test type `flow_tests_details::Int`, `Tracker`, and numerous `TEST_CASE`s under `/flow`, `/fdbrpc`, and `/flow/thread`.

## Control Flow
Early tests validate actor line-number preservation, buggified delay ordering, future/promise/stream readiness and callbacks, cancellation propagation, simple actor return/wait/choose behavior, quorum, and networked serialization of request streams. Yielded-future tests replace `g_network` with `YieldMockNetwork` and verify readiness throttling. Performance tests create one million actors/futures under several patterns. AsyncMap/YieldedAsyncMap tests run randomized operations and basic/cancel cases. Later tests cover actor compiler class-context parsing, deterministic random signed bounds, PromiseStream move/copy behavior, randomized `FlowMutex` locking with injected errors, `ThreadReturnPromiseStream` sequencing/error/destruction behavior, and `waitValueOrSignal` peer-disconnect retry cases.

## State and Persistence Behavior
The tests mutate only process-local test state, Flow futures/promises, mock network globals, local peer objects, and thread-pool queues. `YieldMockNetwork` temporarily replaces `g_network` and restores it in the destructor. No durable external state is written.

## Dependencies and Integration Points
It depends on Flow actor compiler, Arena, Error, ProtocolVersion, UnitTest, DeterministicRandom, thread pools, WriteOnlySet, fdbrpc transport primitives, TLS config, `AsyncTaskExecutor`, and `Peer`/`waitValueOrSignal` behavior. It is a central regression suite for Flow primitives used throughout FoundationDB.

## Risks and Edge Cases
Several performance tests are intentionally heavy. Randomized tests depend on deterministic randomness but still cover a bounded subset of interleavings. `YieldMockNetwork` delegates most methods manually, so additions to `INetwork` may require updates. Some tests intentionally inspect moved-from objects or broken promises. Fixed assumptions about error codes (`request_maybe_delivered`, `broken_promise`, `end_of_stream`) encode important fdbrpc retry semantics and can fail if error mapping changes.

## Test Signals
Passing this file is a strong signal that actor compiler transformations, callback lifetimes, cancellation, PromiseStream move semantics, FlowMutex error propagation, thread-to-Flow stream delivery, and peer-disconnect retry handling behave correctly. The final `waitValueOrSignal` tests specifically guard against hangs when a peer disconnects before failure monitor signals fire.
