# sources/storage-engines/foundationdb/flow/genericcoros.h

Purpose: header-only C++20 coroutine implementations of common Flow future combinators.

Important APIs/types/functions: namespace `generic_coro`; templates `traceAfter`, `stopAfter`, `throwErrorOr`, `transformErrors`, `transformError`, `waitForAllReady`, `timeout` overloads, `timeoutError`, `delayed`, `trigger`, `uncancellable`, `holdWhile`, and `store`.

Control flow: functions use `co_await`, `race`, `delay`, and `coro::errorOr` to mimic actor utilities. Error handling preserves actor cancellation in transform paths, optionally logs trace events, and returns optional/timed-out values when delay wins.

State/persistence: no global state. `stopAfter` calls `g_network->stop()` after completion/error. `uncancellable` uses an intermediate promise to shield the underlying future.

Dependencies/integration: includes `flow/Coroutines.h` and `flow/flow.h`; benchmark and unit-test files compare these helpers with actor implementations.

Risks: templates are instantiated broadly and are sensitive to `Future<T>` move/copy semantics. `waitForAllReady` ignores result errors intentionally by awaiting `errorOr(ignore(result))`. `timeout` races may cancel losers depending on Flow race behavior.

Test signals: tests in `genericactors.actor.cpp` and benchmarks in `BenchTimeout.cpp`/`BenchWaitForAllReady.cpp`.
