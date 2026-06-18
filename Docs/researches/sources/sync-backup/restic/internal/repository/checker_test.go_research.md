## sources/sync-backup/restic/internal/repository/checker_test.go

Purpose: targeted tests for repository pack verification and error classification.

Important helpers/tests: `testWrapCheckPack` creates shared buffers/zstd decoder for `checkPack`. `TestGapInBlobs` removes an indexed blob entry and expects `ErrPackData` containing gap/overlap and header-size messages. `collectErrors` and `runReadPacks` gather asynchronous checker errors. Backend wrappers `lastByteFlipBackend`, `alwaysFailBackend`, and `truncatingBackend` simulate corruption, total download failure, and partial reads. `setupChecker` writes a test snapshot, reopens through a wrapper, and loads indexes. `TestCheckPackHashMismatch`, `TestCheckPackDownloadError`, and `TestCheckPackPartialDownloadError` verify error classification.

Control flow and state: tests mutate the read path rather than on-disk fixtures when possible, allowing controlled corruption without editing repository data. Some tests use a fixed tar fixture for known pack/blob layout.

Dependencies and integration points: integrates archiver snapshot creation, backend wrapping, repository test helpers, zstd setup, and checker internals.

Risks and test signals: these tests protect repair-command behavior by ensuring total network/backend failures are not mislabeled as repairable pack corruption, while partial reads are. They do not exhaustively cover duplicate pack hints or mixed-pack detection.
