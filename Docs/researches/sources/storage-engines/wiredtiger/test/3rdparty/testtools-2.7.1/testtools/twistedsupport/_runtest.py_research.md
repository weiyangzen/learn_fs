<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_runtest.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_runtest.py

Purpose: Testtools `RunTest` implementations for test cases whose setup, test method, teardown, or cleanups return Twisted `Deferred`s.

Important APIs/types/functions: `SynchronousDeferredRunTest` runs already-fired deferreds without the reactor. `AsynchronousDeferredRunTest` spins a reactor through `Spinner`, captures Twisted logs, flushes logged errors, runs async cleanups, and reports success only after reactor cleanup. `AsynchronousDeferredRunTestForBrokenTwisted` adds obligatory reactor iterations. `CaptureTwistedLogs`, `flush_logged_errors`, `run_with_log_observers`, `assert_fails_with`, and `UncleanReactorError` support logging and assertion behavior.

Control flow: Async runs call setup, test, teardown, forced failure checks, and cleanups through deferred chains; `_blocking_run_deferred` translates spinner timeout/no-result into test failures; unhandled deferred errors and reactor junk become test errors.

State and persistence behavior: Temporarily sets `case.reactor`, mutates Twisted log observers, records details on the test case, and manages global `_log_observer`.

Dependencies and integration points: Depends on Twisted reactor/log/trial internals, fixtures, and testtools `RunTest`; exposed by `twistedsupport`.

Risks and test signals: Sensitive to Twisted private APIs, global log observers, timeouts, and reactor cleanup. Tests should cover timeout, logged errors, unhandled deferred failures, async cleanup failures, and stale reactor junk.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_runtest.py -->
