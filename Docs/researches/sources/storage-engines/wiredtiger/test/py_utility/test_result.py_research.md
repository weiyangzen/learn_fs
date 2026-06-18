# sources/storage-engines/wiredtiger/test/py_utility/test_result.py

Purpose: custom `unittest` text result that prefixes verbose output and error lists with process IDs, including child process IDs conveyed through test tags.

Important APIs and control flow: `PidAwareTextTestResult` subclasses `unittest.TextTestResult`. The constructor initializes a thread-local prefix with the current PID. `tags()` detects new tags like `pid:<child>` and updates the prefix to `[pid:parent/child]: `. `startTest()` writes the prefix before delegating to the superclass. `getDescription()` returns `test.shortDescription()`, and `printErrorList()` writes separator lines plus PID-prefixed errors.

State and persistence behavior: state is per-result and per-thread through `threading.local()`. It writes only to the configured unittest stream.

Dependencies and integration points: integrates with test runners that emit tags, especially parallel/concurrent test execution where child PID attribution matters.

Risks: prefix state is thread-local but tag interpretation assumes `pid:` tags arrive before output that needs the child prefix. `shortDescription()` may be `None` for tests without descriptions, so stream rendering depends on `str(None)` behavior.

Test signals: verbose test output should show consistent PID prefixes, and failures/errors should be attributable to the correct child process.
