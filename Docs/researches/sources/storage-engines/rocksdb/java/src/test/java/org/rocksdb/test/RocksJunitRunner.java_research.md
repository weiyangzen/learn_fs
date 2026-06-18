# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/test/RocksJunitRunner.java

Purpose: Custom command-line JUnit runner for RocksJava that prints class-level progress and per-method status, then exits with distinct failure codes.

Important APIs/types/functions: `RocksJunitRunner.main`, nested `RocksJunitListener extends TextListener`, `testRunStarted`, `testStarted`, `testFailure`, `testIgnored`, `testFinished`, `testRunFinished`, `printTestsSummary`, and `Status` enum.

Control flow and state: `main` converts class-name arguments to `Class<?>`, registers the listener on `JUnitCore`, runs all classes, exits `-1` on test failure or `-2` on class lookup failure. The listener tracks current class/method, status, start time, and counters. On class changes it prints the previous class summary, then starts a new block. Failures are split into assertion failures and errors by exception type.

State and persistence behavior: all state is process-local counters and current-test metadata. No test results are persisted except stdout/stderr and process exit status.

Dependencies and integration points: uses JUnit internals (`RealSystem`, `TextListener`), `JUnitCore`, and imports `RocksDB` only to keep RocksJava context available. Intended for build/test scripts.

Risks: relies on JUnit internal classes and mutable listener state; parallel JUnit execution would make counters unsafe. `testIgnored` can set status without `testStarted` establishing method state for some JUnit flows.

Test signals: no dedicated tests here; behavior is observable when running RocksJava test suites.
