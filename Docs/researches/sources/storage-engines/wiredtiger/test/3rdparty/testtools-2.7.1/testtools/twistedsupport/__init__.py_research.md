<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/__init__.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/__init__.py

Purpose: Public facade for vendored `testtools.twistedsupport`.

Important APIs/types/functions: Re-exports `succeeded`, `failed`, `has_no_result`, `AsynchronousDeferredRunTest`, `AsynchronousDeferredRunTestForBrokenTwisted`, `SynchronousDeferredRunTest`, `CaptureTwistedLogs`, `assert_fails_with`, and `flush_logged_errors`.

Control flow: Import-only module; consumers receive symbols from `_matchers` and `_runtest`.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Integrates Twisted `Deferred` assertions and test runners into the bundled testtools package. WiredTiger receives it as third-party test infrastructure rather than production code.

Risks and test signals: Public `__all__` controls compatibility. Missing or renamed imports break downstream tests at import time; import smoke tests with Twisted installed are the main signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/__init__.py -->
