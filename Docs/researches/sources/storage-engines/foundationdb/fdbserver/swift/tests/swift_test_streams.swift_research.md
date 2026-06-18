# sources/storage-engines/foundationdb/fdbserver/swift/tests/swift_test_streams.swift

Purpose: Exercises Swift async integration with Flow `PromiseStream`/`FutureStream`, including direct `waitNext`, `AsyncSequence` iteration, a Swift task-group equivalent of Flow `loop choose`, and actor/task fanout from multiple streams.

Important APIs/types/functions: `StreamTests: SimpleSwiftTestSuite` contributes four `TestCase`s. The tests use generated C++ bridge types `PromiseStreamCInt`, `FutureStreamCInt`, `PromiseVoid`, `FlowClock`, and `end_of_stream()`. `sleepALittleBit()` uses the Flow clock for deterministic sleeps.

Control flow: The first test sends values into a promise stream, checks immediate readiness/pop behavior, then awaits `waitNext`. The second test starts a producer task, sends three integers, terminates with `end_of_stream`, and consumes the stream through `for try await`. The task-group test races a sleep task and a future-wait task, repeats sleep notifications until the promise completes, cancels outstanding tasks, and verifies the ready value. The final test starts two stream-consumer tasks, each spawning child tasks into a Swift `actor Cook`; a promise completes when all expected cook calls finish.

State and persistence behavior: All state is in-memory: stream queues, task-local variables, the `Cook` actor counters, and a promise used as a completion latch. No database or file state is touched.

Dependencies and integration points: Imports `Flow` and `flow_swift`. It validates generated Swift conformances from Flow stream bridging and the custom Flow clock/executor behavior used by FoundationDB's Swift interop layer.

Risks: Cancellation of stream-consuming tasks is explicitly noted as incomplete, so deferred task cancellation may not interrupt a blocked stream await. Nested unstructured `Task` creation can outlive local scope if completion accounting regresses. The tests rely on deterministic single-threaded Flow scheduling assumptions.

Test signals: Uses `precondition` assertions for values and actor results, plus end-of-stream termination and completion promise fulfillment. Failures manifest as thrown async errors, precondition traps, or hangs.
