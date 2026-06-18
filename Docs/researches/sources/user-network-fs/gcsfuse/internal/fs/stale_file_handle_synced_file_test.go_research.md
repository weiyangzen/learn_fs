<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_synced_file_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_synced_file_test.go

Purpose: non-streaming stale-handle coverage for files that start as existing GCS objects.

Important APIs/types/functions: suite `staleFileHandleSyncedFile`; `SetupTest`; tests for clobbered read, clobbered first write, renamed-file write, and remote deletion before sync/close.

Control flow: setup creates a GCS object and opens it for read/write direct I/O. Tests replace, rename, or delete the backing object, then perform reads/writes/sync/close and assert ESTALE or success depending on whether data was accepted.

State and persistence behavior: handle state includes object generation at open. Reads and first writes detect generation mismatch. A failed first write leaves no dirty state, so sync/close can succeed. Dirty data followed by remote deletion fails on sync/close and preserves the deleted/clobbered state.

Dependencies and integration points: uses storageutil for remote mutation, `os.Rename` through mount, and operations helpers for ESTALE and object validation. Exercises file read, write, sync, close, and rename invalidation paths.

Risks: stale reads must fail rather than returning data from an object no longer matching the handle. Sync must not overwrite remote clobbers or resurrect remote deletions, while local unlink semantics from the common suite remain different.

Test signals: ESTALE on clobbered read, ESTALE on clobbered first write with clean sync, ESTALE on write after rename, and ESTALE on sync/close after remote deletion of a dirty handle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_synced_file_test.go -->
