# sources/sync-backup/kopia/snapshot/upload/upload_test.go

## Purpose
Unit/integration tests for the snapshot upload package using real repository writers, mock filesystems, virtual filesystems, faulty blob storage, fake time, and captured logs.

## Important APIs, Types, and Functions
`uploadTestHarness` creates a filesystem-backed repository wrapped in faulty/logging storage and a populated `mockfs.Directory`. Helpers include `findAllEntries`, `verifyMetadataCompressor`, `verifyErrors`, `randomBytes`, `verifyFileContent`, `verifyContainsOffset`, `mockProgress`, `mockLogger`, `loggedAction`, and `verifyLogDetails`.

## Control Flow
Tests build repositories, run `NewUploader(...).Upload` under different policies and source trees, then inspect manifests, stats, repository content metadata, restored entries, blob call concurrency, and captured uploader logs. Some tests use fake ticker/checkpoint channels to deterministically trigger checkpointing, while large parallel tests use real temp files and are skipped unless suitable for CI/Linux AMD64.

## State and Persistence Behavior
Each harness initializes an on-disk Kopia repository and write session. Tests write snapshots, content blobs, directory manifests, checkpoint manifests, and sometimes flush repositories. Mock filesystem hooks inject readdir/open failures and cancellation points. Log tests install a context logger and force `ParallelUploads=1` for stable order.

## Dependencies and Integration Points
Touches most upload dependencies: `repo`, filesystem blob storage, content compression, snapshot manifests, policy trees, `snapshotfs`, `mockfs`, `virtualfs`, `localfs`, `workshare` behavior through uploader knobs, and blob fault instrumentation.

## Risks
Some tests are resource-heavy (`TestParallelUploadDedup`, `TestParallelUploadOfLargeFiles`) and gated. Parallel tests share package globals only through logging/time utilities, so order is mostly isolated. Logging assertions are intentionally strict and can fail on output schema changes. Random data tests depend on repository size heuristics.

## Test Signals
Coverage includes cache stability across snapshots, metadata compression headers, top-level versus child read failures, ignored/fatal error summaries, child error policy, progress callbacks for successes/errors/cache, symlink summaries, checkpoint retention labels, parallel upload concurrency, streaming files/directories, compression with streaming files, dedup of identical large files, large-file part concatenation offsets/content, and log-detail keys/messages.
