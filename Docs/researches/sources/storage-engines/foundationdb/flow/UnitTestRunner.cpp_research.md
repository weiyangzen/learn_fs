<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/UnitTestRunner.cpp -->
# sources/storage-engines/foundationdb/flow/UnitTestRunner.cpp
- Purpose: Command-line runner for Flow `TEST_CASE`s linked into a target, with optional simulation mode.
- Important APIs/types/functions: `UnitTestRunnerConfig`, `runUnitTests`, `parseArgs`, `collectTests`, `testMatched`, `runTests`, `runTestsAfterInitialization`, and `stopNetworkAfter`.
- Control flow: `runUnitTests()` initializes platform/errors/randomness, parses options, creates a temporary run directory, initializes either Sim2 or Net2, opens a trace file, schedules test execution, runs the network, flushes traces, reports pass/fail counts, and removes the run directory. Test execution filters by suite path and name prefix, optionally lists tests, limits count, runs each test with a data directory, logs `RunningUnitTest` and final `UnitTest` events, and records failures from thrown Flow errors.
- State and persistence behavior: Uses process globals `g_unittests`, `g_network`, deterministic random seed, temporary `/tmp/<suite>.<pid>.<seed>` directories, per-test data directories, and trace files capped at 10 MiB roll/size settings.
- Dependencies and integration points: Depends on `SimpleOpt`, `fmt`, Flow platform/network/TLS/trace/random/error/unit-test APIs, and optional simulation initializer supplied by the target.
- Risks: Path filtering requires test source files to include the suite component. Empty matches are treated as failure unless listing. Cleanup erases test data unless `--no-cleanup`. The runner changes CWD and only cleans the run directory after successfully changing back.
- Test signals: CLI behavior can be validated with `--list`, `--filter`, `--ignore`, `--seed`, `--max-test-cases`, simulation support checks, failure counting, and trace-file creation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/UnitTestRunner.cpp -->
