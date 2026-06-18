# File Research: sources/windows/reactos/drivers/filesystems/udfs/cleanup.cpp

## Purpose
Handles IRP cleanup for the UDFS driver. Cleanup is where open handles are retired, share access is removed, byte-range locks are cleared, delete-on-close is processed, cache maps are flushed/uninitialized, timestamps and directory-index metadata are updated, and file-info chains are closed.

## Main Contents
- `UDFCleanup` is the dispatch entry point:
  - Handles cleanup against the filesystem device object directly.
  - Allocates IRP context for volume/file cleanup.
  - Uses top-level IRP tracking and structured exception handling.
- `UDFCommonCleanup` performs the main cleanup work:
  - Extracts `FileObject`, `Ccb`, `Fcb`, `Vcb`, and NT-required FCB data.
  - Handles volume cleanup separately, including handle counts, verify-volume flag, lock release, cache-map uninitialization, optional device reset, and share-access removal.
  - Acquires parent/current FCB resources for file cleanup.
  - Decrements open-handle and VCB-handle counts.
  - Processes `UDF_CCB_DELETE_ON_CLOSE` into `UDF_FCB_DELETE_ON_CLOSE`.
  - Unlocks all byte-range locks for non-directory files.
  - Handles stream deletion marking and parent deletion propagation.
  - Flushes/unlinks files on delete-on-close when last handle closes.
  - Issues directory/file/stream notifications for delete or modification.
  - Flushes/purges cache sections when needed.
  - Updates archive bit, write/access/change times, and directory-index file sizes.
  - Calls `CcUninitializeCacheMap`.
  - Releases resources and calls `UDFCloseFileInfoChain`.
  - Removes share access, recalculates fast-I/O possibility, and marks `FO_CLEANUP_COMPLETE`.
- `UDFCloseFileInfoChain` walks up a file-info parent chain:
  - Acquires parent/current resources.
  - Writes security when needed.
  - Calls `UDFCloseFile__` for each file info.
  - Releases resources as it climbs toward root.

## Dependencies and Interactions
- Uses Windows filesystem APIs: `FsRtlEnterFileSystem`, `IoCompleteRequest`, `FsRtlFastUnlockAll`, `FsRtlNotifyCleanup`, `FsRtlNotifyFullChangeDirectory`, `CcFlushCache`, `CcPurgeCacheSection`, `CcUninitializeCacheMap`, and `IoRemoveShareAccess`.
- Coordinates tightly with UDFS FCB/CCB/VCB lifetime, delete-on-close, stream directory handling, delayed/system close queues, and notification logic.
- Calls many UDFS helpers: `UDFFlushFile__`, `UDFUnlinkFile__`, `UDFMarkStreamsForDeletion`, `UDFPretendFileDeleted__`, `UDFCloseFileInfoChain`, `UDFSetFileXTime`, `UDFSetFileSizeInDirNdx`, and `UDFCloseFile__`.

## Notable Details
- Cleanup and close are split: cleanup handles handle-visible semantics and cache/share cleanup; close handles object lifetime.
- Delete-on-close has special stream and linked-file behavior; multi-link files avoid forced cache purge.
- The function carefully releases and reacquires resources around deletion and close-chain operations to avoid holding incompatible locks.
