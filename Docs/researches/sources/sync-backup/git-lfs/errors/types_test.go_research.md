<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/types_test.go -->
# sources/sync-backup/git-lfs/errors/types_test.go

## Research

This file tests retriable classification for `*url.Error`. Custom `TemporaryError` and `TimeoutError` types implement the legacy `Temporary()` and `Timeout()` methods; the tests assert they are retriable, while a generic wrapped error is not.

The tests are focused and pure. They protect the fallback path in `IsRetriableError` that uses `Cause(err).(*url.Error)` and checks network-transient methods. Gaps include explicit `NewRetriableError`, retry-after parsing, nested wrappers, joined errors, and modern `net.Error` behavior beyond the small fake types.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/types_test.go -->
