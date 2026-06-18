# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/Tester2.java

## Purpose
`Tester2.java` is a reflection-driven sanity and regression suite for the SQLite JNI wrapper1 layer. It can run tests once, repeatedly, shuffled, quietly, with optional naps, with config/sql logging, and concurrently across multiple Java threads.

## Important APIs, types, and functions
- Annotations `@ManualTest` and `@SingleThreadOnly` control reflection-based inclusion.
- Harness state includes `mtMode`, `takeNaps`, `shuffle`, `listRunTests`, `quietMode`, `nTestRuns`, `testMethods`, shared `listErrors`, and `metrics.dbOpen`.
- `affirm()` is the assertion primitive; `out()`/`outln()` provide synchronized logging.
- `execSql()` prepares and steps all SQL statements with `Sqlite.prepareMulti()` and can either throw or return SQLite error codes.
- Test methods cover open/config, prepare/bind/columns, UDFs, window functions, keywords, explain, trace, status, auto-extension, backup, collation, busy handling, commit/rollback/update hooks, progress, authorizer, blob I/O, and multi-statement preparation.
- `main()` parses CLI flags, builds the test method list by reflection, executes serially or through `ExecutorService`, prints metrics, optionally dumps JNI internals, releases memory, shuts SQLite down, and counts `CApi.sqlite3_*` methods.

## Control flow
`main()` parses arguments, installs optional SQL/config logging callbacks, discovers `test*` methods excluding manual and thread-incompatible tests, then loops for `-repeat`. Serial mode calls `runTests(false)` directly; multithread mode submits `Tester2` runnables, collects exceptions in `listErrors`, and rethrows the first failure. Each `run()` calls `Sqlite.uncacheThread()` in `finally` to release thread-local JNI resources.

## State and persistence behavior
Most test data uses in-memory databases, but `testBusy()` creates and deletes `_busy-handler.db`. Static counters and lists accumulate across loops and threads. Each test is responsible for closing database, statement, backup, and blob handles; many use try-with-resources while older paths close explicitly.

## Dependencies and integration points
The suite depends on `Sqlite`, `ValueHolder`, `ScalarFunction`, `AggregateFunction`, `WindowFunction`, `SqlFunction.Arguments`, Java reflection/concurrency utilities, and `CApi`. It directly validates behavior promised by `Sqlite.java` and JNI support for Java object binding, Unicode round trips, and native callback adapters.

## Risks and edge cases
- `ExecutorService.awaitTermination(nThread*200ms)` may be short under slow or instrumented environments and then calls `shutdownNow()`.
- Static counters and mutable lists are shared across threads; operations that mutate test list/order are done before execution, and error list is synchronized only around insertion/reading in key places.
- Some tests are sensitive to SQLite build options, VFS behavior, filesystem permissions, and timing.
- `testBusy()` increments `metrics.dbOpen` both inside `openDb(name)` and manually, apparently double-counting for those opens.

## Test signals
This file is itself the test signal for wrapper1. Successful output reports assertions checked, databases opened, SQLite version/source id/threadsafe mode, `CApi.sqlite3_*` method counts, and elapsed time. The `-fail` flag intentionally injects a failure path into reflected test execution.
