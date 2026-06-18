<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_local_file_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_local_file_test.go

Purpose: runs the common non-streaming stale-handle suite for a local-only file that has not yet been synced to GCS.

Important APIs/types/functions: suite `staleFileHandleLocalFile`; `SetupTest`; `TestStaleFileHandleLocalFile`.

Control flow: each test creates a local file through `operations.CreateLocalFile`, stores the open handle in `t.f1`, and then inherits the common clobber and local-delete tests from `staleFileHandleCommon`.

State and persistence behavior: starts with local inode/file state and no GCS object, then tests introduce or validate GCS object state depending on the common helper. This checks promotion from local-only state under conflict.

Dependencies and integration points: depends on shared stale-handle common tests, local file creation helpers, file sync behavior, and fake bucket validation.

Risks: local-only files do not have an original generation at creation time, so conflict detection must still prevent overwriting a remote object that appears before sync.

Test signals: inherited tests prove local files report ESTALE after remote clobber and do not recreate a file after local unlink followed by sync/close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_local_file_test.go -->
