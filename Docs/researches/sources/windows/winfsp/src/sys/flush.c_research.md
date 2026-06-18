# File Research: sources/windows/winfsp/src/sys/flush.c

## Role

Implements `IRP_MJ_FLUSH_BUFFERS` for WinFsp filesystem volumes. It flushes kernel cache state locally, then posts a flush transaction to the user-mode filesystem so backing storage can be synchronized.

## Main Flow

`FspFlushBuffers` dispatches only for `FspFsvolDeviceExtensionKind`; other device kinds return `STATUS_INVALID_DEVICE_REQUEST`.

`FspFsvolFlushBuffers` has two modes:

- Volume/root flush: if `FileObject->FsContext` is not a valid file node or the file node is the root directory, this is treated as a whole-volume flush.
- File flush: for regular file nodes, it flushes that file’s cache and posts a per-file user-mode flush.

For a whole-volume flush, the code copies the list of open file nodes using `FspFileNodeCopyOpenList`, clears the top-level IRP to avoid resource deadlocks, flushes non-directory file cache sections in reverse list order, restores the top-level IRP, deletes the copied list, then creates a request with a null user context. The null context is the protocol signal for “flush whole volume.” It records the local flush result in request context.

For a file flush, directories succeed immediately because there is no meaningful directory cache flush. Regular files are acquired exclusive with full locking, `FspCcFlushCache` is called on the file object section pointers, and a `FspFsctlTransactFlushBuffersKind` request is posted with both user contexts. The file node is marked as owner-held by the request so cancellation/finalization can release it.

## Completion

`FspFsvolFlushBuffersComplete` combines two result sources:

- The user-mode response status.
- The local cache flush result saved in request context for whole-volume flushes.

If both succeed and this is a real file node rather than volume/root, it updates file info from `Response->Rsp.FlushBuffers.FileInfo` with truncate-on-close enabled.

`FspFsvolFlushBuffersRequestFini` releases owner-held file-node locks when a posted per-file request is canceled or otherwise finalized before normal completion.

## Integration Points

This file uses `file.c` for open-list copying, full-resource acquisition, owner release, and file-info updates. It uses `iop.c` request creation/finalization and the WinFsp transaction kind consumed by user-mode dispatch.

## Edge Cases And Risks

- Whole-volume flush intentionally resets `IoSetTopLevelIrp(0)` during local cache flushes to avoid recursive resource deadlocks.
- Reverse-order volume flush is intended to flush children before containing directories, although directories are skipped.
- Directory flush returns success without posting to user mode.
