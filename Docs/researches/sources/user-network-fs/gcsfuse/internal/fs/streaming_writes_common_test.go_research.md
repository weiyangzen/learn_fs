<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/streaming_writes_common_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/streaming_writes_common_test.go

Purpose: shared integration tests for streaming-write semantics used by local files and empty synced GCS objects.

Important APIs/types/functions: suite `StreamingWritesCommonTest`; tests `TestUnlinkBeforeWrite`, `TestUnlinkAfterWrite`, `TestRenameFileWithPendingWrites`, `TestTruncateToLowerSizeSyncsFileToGcs`, `TestTruncateToLowerSizeSyncsFileToGcsAndDeletingFileDeletesFromGcs`, `TestOutOfOrderWriteSyncsFileToGcs`, and `TestOutOfOrderWriteSyncsFileToGcsAndDeletingFileDeletesFromGcs`.

Control flow: tests operate on `t.f1` supplied by child suites. They unlink before/after writes, rename a dirty handle, truncate after writing, issue out-of-order `WriteAt`, and then read GCS contents or mounted file content to validate when final data becomes durable.

State and persistence behavior: streaming writes initially upload or buffer sequential data. Truncate to lower size and out-of-order writes force the file into a synced/finalized state on close, with GCS showing old streamed data before close and final content after close. Deleting after forced sync removes the object from GCS.

Dependencies and integration points: depends on child suite setup for streaming write config, storageutil object reads, `gcs.NotFoundError`, and integration `operations`.

Risks: rename/unlink with pending streaming writes can leave temporary objects, stale handles, or resurrected GCS objects if ordering is wrong. Out-of-order writes and truncation are critical fallback paths from streaming append to full object rewrite.

Test signals: unlink removes local/GCS state, rename flushes pending writes to the new name, truncate and out-of-order writes preserve previous GCS content until close then finalize correct content, and delete after fallback sync removes GCS object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/streaming_writes_common_test.go -->
