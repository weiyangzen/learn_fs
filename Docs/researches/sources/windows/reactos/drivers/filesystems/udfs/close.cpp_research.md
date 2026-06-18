# File Research: sources/windows/reactos/drivers/filesystems/udfs/close.cpp

## Purpose
Handles IRP close for the UDFS driver. Close is responsible for freeing CCBs, decrementing open/reference counts, queueing or executing delayed close, cleaning FCB/file-info chains, processing final volume close/dismount checks, and flushing/purging delayed-close objects in directories.

## Main Contents
- `UDFClose` is the close dispatch entry:
  - Handles filesystem-device-object closes directly.
  - Allocates IRP context.
  - Invokes `UDFCommonClose` under top-level IRP and exception handling.
- `UDFCommonClose`:
  - Extracts `FileObject`, `Ccb`, `Fcb`, and `Vcb` for normal IRP close, or uses saved FCB/tree length for queued close.
  - Cleans and detaches the CCB.
  - Attempts delayed close when enabled and eligible.
  - Posts recursive/not-top-level close work when needed.
  - Decrements CCB count and VCB open counts.
  - Handles volume close specially, including global/Vcb resource ordering, write-status reset IOCTL, and dismount checks.
  - For file closes, calls `UDFCleanUpFcbChain`.
  - Completes IRP and releases IRP context unless posted.
- `UDFCleanUpFcbChain`:
  - Walks from a file-info node toward the root.
  - Decrements references for the open path.
  - Flushes files before final cleanup.
  - Handles delete-parent propagation.
  - Clears `fi->Fcb` and common-FCB links before lower-level cleanup.
  - Frees NT-required FCB resources, byte-range lock structures, ACL state, FCBs, and file-info allocations when safe.
  - Stops when it reaches referenced objects.
- Delayed-close machinery:
  - `UDFDoDelayedClose` converts a lite context back to a full IRP context and calls `UDFCommonClose`.
  - `UDFDelayedClose` drains file and directory delayed-close queues down to configured minimums.
  - `UDFCloseAllDelayed` drains all delayed closes for a VCB.
  - `UDFQueueDelayedClose` creates lite close contexts, inserts them into file or directory queues, tracks thresholds, and queues worker work.
- Directory subtree delayed-close support:
  - `UDFBuildTreeItemsList` recursively walks stream directories and directory indexes, avoiding repeated linked objects.
  - `UDFIsInDelayedCloseQueue` and `UDFIsLastClose` are selection callbacks.
  - `UDFCloseAllXXXDelayedInDir` finds delayed or system-cache-backed objects under a directory, then either flushes/purges system cache sections or removes internal delayed-close queue entries.

## Dependencies and Interactions
- Uses filesystem and memory-manager/cache-manager APIs such as `CcFlushCache`, `CcPurgeCacheSection`, `MmFlushImageSection`, and worker queue APIs.
- Coordinates with global delayed-close queues in `UDFGlobalData`.
- Calls UDFS-specific object lifetime helpers such as `UDFCleanUpCCB`, `UDFCleanUpFCB`, `UDFCleanUpFile__`, `UDFCloseFile__`, `UDFFlushFile__`, `UDFUnlinkFile__`, `UDFCheckForDismount`, and IRP-context lite conversion helpers.
- Uses `IOCTL_CDRW_RESET_WRITE_STATUS` on final volume close.

## Notable Details
- Close always returns success to the I/O manager, as expected for filesystem close dispatch.
- Delayed close is suppressed for delete-on-close and posted-rename FCBs.
- `UDFBuildTreeItemsList` allocates growing arrays in `TREE_ITEM_LIST_GRAN` chunks and avoids repeated traversal of linked file-info objects.
- `UDFCloseAllXXXDelayedInDir` can operate in “system” mode to flush/purge cache sections, or internal mode to drain delayed-close queue entries.
