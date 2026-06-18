# sources/sync-backup/git-lfs/tq/errors_test.go

Purpose: tests `MalformedObjectError` classification.

Important APIs/types/functions: `TestMissingObjectErrorsAreRecognizable` and `TestCorruptObjectErrorsAreRecognizable`.

Control flow: creates errors via constructors, type asserts to `*MalformedObjectError`, and checks name/OID plus `Missing` or `Corrupt`.

State and persistence: none.

Dependencies and integration points: validates upload preflight error semantics.

Risks: does not assert formatted `Error()` strings.

Test signals: focused coverage for type fields/classification.
