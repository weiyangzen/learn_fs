<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_spinner.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_spinner.py

Purpose: Low-level reactor spinner used to run asynchronous Twisted tests inside synchronous testtools control flow.

Important APIs/types/functions: `not_reentrant`/`ReentryError` prevent recursive spinner entry. `trap_unhandled_errors` monkey-patches `defer.DebugInfo` to collect unhandled deferred failures. `Spinner.run` schedules the user function, spins the reactor until completion or timeout, restores signals and `reactor.stop`, and cleans delayed calls/selectables/threadpool. Exceptions include `TimeoutError`, `NoResultError`, and `StaleJunkError`.

Control flow: `run` saves signal handlers, schedules timeout and test function, substitutes `reactor.stop` with `crash`, starts the reactor, extracts success/failure, then cancels leftover reactor resources into `_junk`.

State and persistence behavior: Maintains `_success`, `_failure`, `_timeout_call`, `_saved_signals`, `_junk`, and `_spinning`; no persistence across process runs.

Dependencies and integration points: Uses Twisted reactor, `IReactorThreads`, `Failure`, and `DebugTwisted`; consumed by `_runtest`.

Risks and test signals: Global monkey-patching and reactor mutation are fragile. Tests need coverage for timeout, nested run rejection, signal restoration, stale junk detection, and threadpool cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_spinner.py -->
