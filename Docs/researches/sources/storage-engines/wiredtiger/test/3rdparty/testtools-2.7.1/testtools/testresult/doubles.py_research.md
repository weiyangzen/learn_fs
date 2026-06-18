# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/testresult/doubles.py

Purpose: lightweight fake result objects for testing unittest/testtools result interactions.

Important APIs, types, and functions: `LoggingBase` stores an event log. `Python26TestResult`, `Python27TestResult`, `ExtendedTestResult`, `TwistedTestResult`, and `StreamResult` emulate increasing result API capabilities. `_StatusEvent` is a namedtuple for stream events.

Control flow: each result method appends a tuple or `_StatusEvent` to `_events`. Python 2.7-style failfast calls `stop()` on errors/failures/unexpected success. `ExtendedTestResult` tracks nested `TagContext` objects around test start/stop and logs details-enabled outcomes. `StreamResult.status()` records all stream status fields.

State and persistence: state is the in-memory event list, `shouldStop`, success flag, test count, and current tag context. No persistence.

Dependencies and integration points: depends on `collections.namedtuple` and `testtools.tags.TagContext`. Used by testtools' own tests and by vendored packages such as testscenarios through `LoggingResult`-style event assertions.

Risks and test signals: these doubles intentionally implement only relevant API subsets; using them as production results would miss formatting and concurrency behavior. Test signals are event ordering, failfast stop behavior, tag scoping, success flags, and stream status field capture.
