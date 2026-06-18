# sources/storage-engines/sqlite/ext/wasm/SQLTester/SQLTester.run.mjs

## Purpose

This module is the executable harness for `SQLTester.mjs`. It imports the SQLTester namespace and the generated test list, creates a tester, runs an embedded sanity-check script, loads all generated SQLTester scripts, and supports both direct main-thread execution and worker-driven execution.

## Important APIs and Functions

The module imports `ns` from `./SQLTester.mjs` and `allTests` from `./test-list.mjs`. It exposes `ns.sqlite3` on `globalThis.sqlite3` for debugging. Local helpers include `log()`, buffered `out`/`outln` backed by `ns.Outer`, `affirm()`, and `runTests()`. The `sqt` instance is a configured `ns.SQLTester` with console logging, verbosity 1, and an initial embedded `TestScript`.

## Control Flow

At load time, the module builds a sanity-check SQLTester script covering print, close, OOM no-op, database selection, new database creation, null rendering, result comparison, glob/notglob, non-fatal run errors, JSON comparison, table-result comparison, JSON block comparison, column-name toggling, and close behavior. `runTests()` then either runs a disabled direct-debug branch or, in normal operation, appends every generated test object from `allTests` as a `TestScript`, clears the imported array, and calls `sqt.runTests()`. A `finally` block resets tester state after the run.

If running in a worker global scope, the module installs an `onmessage` handler. On `run-tests`, it runs tests and posts `tests-end` with metrics. It redirects tester logs to `stdout` messages and sends an initial `is-ready` message. Outside a worker, it runs tests immediately.

## State and Persistence

State is primarily the singleton `sqt` tester and its metrics. Generated test content is released by setting `allTests.length = 0` after scripts are added. Worker mode communicates state through structured messages: `is-ready`, `stdout`, and `tests-end`. Database files and SQLite state are owned by `SQLTester.mjs` and reset after execution.

## Dependencies and Integration Points

This file depends on `SQLTester.mjs`, generated `test-list.mjs`, browser or worker globals, and console logging. It is the runtime counterpart to `SQLTester/GNUmakefile`, which creates the imported test list. In worker mode it integrates with whichever test page or controller posts `run-tests` and consumes stdout and metrics messages.

## Risks and Edge Cases

Because it imports `test-list.mjs` statically, the generated module must exist before this runner loads. The sanity script uses some disabled incompatible directive examples in comments, not as active commands. In worker mode, unknown messages are only logged. If `runTests()` throws before posting metrics, the `finally` in the worker case still posts `tests-end`, but fatal module-load errors before handler setup would not. Main-thread mode runs immediately on import, which is appropriate for a test application but surprising for library-style reuse.

## Test Signals

The embedded sanity script is the first signal that command parsing and basic SQL execution work. Running generated tests from `allTests` is the main regression signal. Worker clients can treat `is-ready` as load success, `stdout` as progress, and `tests-end` metrics as completion evidence.
