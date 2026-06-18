# sources/storage-engines/foundationdb/fdbserver/swift/tests/swift_tests.swift

Purpose: Provides the Swift test-suite registration and C++-visible entry point for the Swift/Flow interop tests.

Important APIs/types/functions: `_mainThreadID` captures `_tid()` at load time. `SimpleSwiftTestSuites` registers `TaskTests` and `StreamTests`. `@_expose(Cxx) public func swiftyTestRunner(p: PromiseVoid)` launches the Swift harness and signals a Flow promise. `assertOnNet2EventLoop()` checks the current thread matches `_mainThreadID`.

Control flow: C++ calls `swiftyTestRunner` with a promise. The function starts a Swift `Task`, awaits `SimpleSwiftTestRunner().run()`, logs any caught error in red, and sends `Flow.Void()` to unblock the caller. Tests call `assertOnNet2EventLoop` after awaits/tasks.

State and persistence behavior: Uses one unsynchronized global `_mainThreadID`; comments state this is safe because tests run single-threaded on Net2. No persistence.

Dependencies and integration points: Imports `Flow` and `flow_swift`, uses `PromiseVoid` and `Flow.Void`, and exposes the function to C++ via Swift interop. Depends on `Rainbow.swift`, `SimpleSwiftTestSuite.swift`, `TaskTests`, and `StreamTests`.

Risks: The promise is sent even after caught runner errors, so callers may see completion rather than failure unless the error crashes or logs are checked. Thread assertion is deliberately tied to single-thread Net2 behavior. The registered suite list must be updated manually when new Swift suites are added.

Test signals: C++ integration observes promise completion; Swift tests emit pass/fail logs and `precondition` traps. `assertOnNet2EventLoop` is a direct executor correctness signal.
