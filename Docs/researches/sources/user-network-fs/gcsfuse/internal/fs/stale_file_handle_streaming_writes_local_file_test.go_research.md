<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_local_file_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_local_file_test.go

Purpose: stale-handle streaming-write coverage for local-only files when a remote object appears or changes before the first streamed write completes.

Important APIs/types/functions: suite `staleFileHandleStreamingWritesLocalFile`; `SetupTest`; test `TestClobberedWriteFileSyncAndCloseThrowsStaleFileHandleError`.

Control flow: creates a local-only file, clobbers the same object name in GCS, generates 4 MiB of data, attempts `WriteAt`, then validates ESTALE on write, sync, and close.

State and persistence behavior: local handle state conflicts with a remote GCS generation created after the handle opened. The test ensures failed writes do not upload local data and that the remote clobber content remains.

Dependencies and integration points: inherits streaming-write setup, uses `operations.CreateLocalFile`, `GenerateRandomData`, ESTALE validation, and `storageutil.ReadObject`.

Risks: local-file streaming write initialization must detect that the name is no longer safe to create. Both write-time and cleanup-time errors must remain consistent.

Test signals: write, sync, and close all return ESTALE, and remote object content is unchanged.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_local_file_test.go -->
