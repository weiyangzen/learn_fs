<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_synced_file_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_synced_file_test.go

Purpose: stale-handle streaming-write coverage for already-synced empty GCS objects, including remote clobber and rename before write.

Important APIs/types/functions: suite `staleFileHandleStreamingWritesSyncedFile`; `SetupTest`; tests `TestWriteToClobberedFileThrowsStaleFileHandleError` and `TestRenameFileWriteThrowsStaleFileHandleError`.

Control flow: setup opens an empty object. One test replaces the object remotely before a 4 MiB `WriteAt`; the other renames the file through the mount before `WriteAt`. Both expect ESTALE on write, while sync/close succeed because no new dirty data was accepted.

State and persistence behavior: original synced object generation and name are tracked by the open handle. Remote replacement or mount rename invalidates that handle for future writes. Existing remote content at the clobbered or renamed name remains unchanged.

Dependencies and integration points: inherits streaming-write common setup and uses object clobber, `os.Rename`, random data generation, ESTALE validation, and storage reads.

Risks: streaming write path must reject writes on stale handles before uploading data. Rename invalidation needs to update handle state and object indexes consistently.

Test signals: write returns ESTALE after clobber or rename, sync/close return nil, and persisted object contents remain the expected empty or clobber data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_synced_file_test.go -->
