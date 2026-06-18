<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_deferreddebug.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_deferreddebug.py

Purpose: Fixture for toggling Twisted debugging in vendored testtools.

Important APIs/types/functions: `DebugTwisted` is a `fixtures.Fixture` that monkey-patches `twisted.internet.defer.Deferred.debug` and `twisted.internet.base.DelayedCall.debug`.

Control flow: `_setUp` installs two `MonkeyPatch` fixtures; fixture cleanup restores original values.

State and persistence behavior: Temporarily mutates Twisted class-level debug flags for the fixture lifetime only.

Dependencies and integration points: Used by `_spinner.Spinner` when async test runners request debug mode.

Risks and test signals: Global class mutation can leak if cleanup fails. Fixture lifecycle tests should verify flags are restored after success and failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/twistedsupport/_deferreddebug.py -->
