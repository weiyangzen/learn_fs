<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/eliotutil.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/eliotutil.py

Purpose: Integrates Eliot structured logging with Tahoe test execution so every test runs inside a named Eliot action and emitted messages are validated.

Important APIs and types: `RUN_TEST` is an Eliot `ActionType` with a test-name field. `EliotLoggedRunTest` composes a delegated `RunTest` factory and patches the actual test method. `with_logging(test_id, test_method)` decorates a callable with a validating `MemoryLogger`. `_TwoLoggers` implements `ILogger` and forwards messages to the original logger plus the validation logger.

Control flow: `EliotLoggedRunTest.run` grabs the test method by `_testMethodName`, wraps it with `with_logging`, monkey-patches it onto the case, invokes the delegated runner, and restores the patch. `with_logging` swaps the global logger to `_TwoLoggers`, opens a `RUN_TEST` action, runs the test, checks Eliot validation errors, and restores the original logger in `finally`.

State and persistence: Temporarily mutates the test case method and Eliot global logger. Validation logs are in-memory and discarded after the test. No filesystem persistence.

Dependencies and integration points: Depends on Eliot, `eliot.testing`, Twisted `MonkeyPatcher`, `attrs`, Zope `ILogger`, `six.ensure_text`, and Tahoe's `AnyBytesJSONEncoder`. Used by `common.py` test case classes as their `run_tests_with` wrapper.

Risks: Global logger swapping is process-wide and sensitive to concurrent test execution. Errors raised during validation occur inside test invocation and can alter failure reporting. `_TwoLoggers` assumes both logger objects implement `write`; a missing original logger would be unsafe if Eliot ever returned `None`.

Test signals: Verify successful log capture, validation failure surfacing, logger restoration on exceptions, delegated runner compatibility, bytes JSON encoding, and test method restoration after repeated runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/eliotutil.py -->
