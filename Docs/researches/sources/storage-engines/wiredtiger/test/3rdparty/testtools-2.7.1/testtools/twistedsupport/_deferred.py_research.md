<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_deferred.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_deferred.py

Purpose: Utility layer for inspecting already-fired Twisted `Deferred` objects in synchronous tests.

Important APIs/types/functions: `DeferredNotFired` reports an unfired deferred. `extract_result` converts a fired deferred into a return value or raised failure. `ImpossibleDeferredError` guards impossible success+failure observations. `on_deferred_result` preserves the deferred result while dispatching to success, failure, or no-result callbacks. `failure_content` converts a Twisted `Failure` to testtools `TracebackContent`.

Control flow: Functions attach callbacks/errbacks that record observed results, then inspect the recorded lists immediately.

State and persistence behavior: State is temporary callback-captured lists; deferred result propagation is preserved by returning captured values.

Dependencies and integration points: Uses Twisted `Failure`/`Deferred` concepts and `testtools.content.TracebackContent`; consumed by `_matchers` and `_runtest`.

Risks and test signals: Designed only for synchronous deferreds; using it with reactor-driven deferreds raises `DeferredNotFired`. Tests should cover success, failure, no-result, and failure traceback detail preservation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_deferred.py -->
