# sources/storage-engines/foundationdb/fdbserver/swift/tests/swift_test_task.swift

Purpose: Verifies Swift async/await behavior for Flow futures and FoundationDB's Swift executor integration, especially resumption on the Net2 event loop and mapping Flow priorities into Swift `Task.priority`.

Important APIs/types/functions: `TaskTests: SimpleSwiftTestSuite` defines tests for `FutureVoid`, `FutureCInt`, broader promise/future await behavior, and Flow task priority. It uses `PromiseVoid`, `PromiseCInt`, `FutureCInt.value()`, `__getUnsafe()`, `Task(priority: .Worker)`, and `assertOnNet2EventLoop()`.

Control flow: The simple tests send into promises before awaiting the future value. The broader test validates not-ready/ready transitions, sends one value before await, sends another from a spawned Swift task, and asserts resumption on the Net2 thread after awaits. The priority test executes a normal child task and a `.Worker` priority task, checking priority raw value and executor location.

State and persistence behavior: State is transient promises/futures and local integers. No database state or durable state is touched.

Dependencies and integration points: Imports `Flow` and `flow_swift`; relies on `_mainThreadID` and `assertOnNet2EventLoop` from `swift_tests.swift`. It tests generated Swift wrappers for Flow futures.

Risks: Uses `try!`, forced unwraps, and `precondition`, so regressions crash rather than produce structured test failures. The test assumes single-threaded Net2 execution and a stable raw priority value of 60 for `.Worker`.

Test signals: Preconditions verify future readiness, returned values, priority values, and executor thread. Printed `pprint` messages provide ordering diagnostics.
