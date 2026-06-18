<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_common_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_common_test.go

Purpose: shared stale-handle tests for the streaming-write path, especially flush/close behavior after a streamed file is clobbered between sync and close.

Important APIs/types/functions: suite `staleFileHandleStreamingWritesCommon`; setup configures `Write.EnableStreamingWrites`, `BlockSizeMb`, `MaxBlocksPerFile`, `GlobalMaxBlocks`, and disables writeback caching; test `TestWriteFileSyncFileClobberedFlushThrowsStaleFileHandleError`.

Control flow: setup enables streaming writes with a small block budget. The test writes 4 MiB at offset 0, calls `Sync`, clobbers the GCS object to a new generation, then closes the file and expects ESTALE.

State and persistence behavior: streaming write state spans local buffers, in-flight uploaded blocks, and final object generation. The test validates that a post-sync close/flush still checks clobber conditions and does not overwrite a newer object.

Dependencies and integration points: uses the common non-streaming config helper, streaming writer configuration, storage utilities, and integration operations for ESTALE validation.

Risks: streaming writes split data upload and finalization; clobbers between stages can corrupt data if close skips generation checks.

Test signals: close returns ESTALE after clobber and remote object content remains the clobber content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_common_test.go -->
