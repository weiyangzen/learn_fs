# sources/sync-backup/git-lfs/tools/iotools_test.go

Purpose: tests `RetriableReader`.

Important APIs/types/functions: `TestRetriableReaderReturnsSuccessfulReads`, `TestRetriableReaderReturnsEOFs`, `TestRetriableReaderMakesErrorsRetriable`, `TestRetriableReaderDoesNotRewrap`, and helper `ErrReader`.

Control flow: wraps successful, EOF, plain-error, and already-retriable readers, then asserts returned bytes/errors.

State and persistence: none.

Dependencies and integration points: validates behavior expected by download code where network read errors should enter transfer retry handling.

Risks: does not cover partial reads with simultaneous data and error, nor `Spool`/`SplitOnNul`.

Test signals: good focused coverage of retry wrapping semantics.
