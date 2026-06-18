<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_matchers.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_matchers.py

Purpose: Matchers for asserting the immediate state and result of synchronous Twisted `Deferred`s.

Important APIs/types/functions: `has_no_result` returns singleton `_NoResult`; `succeeded(matcher)` wraps a matcher against a successful result; `failed(matcher)` wraps a matcher against a Twisted `Failure`. Internal mismatch messages include failure traceback content where useful.

Control flow: Each matcher delegates to `on_deferred_result`, selecting mismatch-producing handlers for unexpected success, failure, or no-result states.

State and persistence behavior: No persistent state; failure matchers add a no-op errback to suppress unhandled failure logging after the matcher has consumed it.

Dependencies and integration points: Builds on `_deferred` and `testtools.matchers.Mismatch`; exposed through `twistedsupport.__init__`.

Risks and test signals: These matchers assume synchronous deferreds. Important tests cover no-result, success mismatch, failure mismatch with traceback detail, and preservation/suppression behavior for Twisted failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_matchers.py -->
