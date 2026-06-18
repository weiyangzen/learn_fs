# File Research: sources/windows/winfsp/src/sys/write.c

This file implements WinFsp write handling for fast I/O, cached IRP writes, non-cached/paging writes, request preparation, completion, cleanup, and dispatch.

Key responsibilities:
- `FspFastIoWrite` handles non-extending cached writes when the file is valid, regular, cache-supported, not write-through, lock/oplock state allows fast I/O, and cache manager write checks pass.
- `FspFsvolWrite` validates the file object, handles MDL write completion, rejects directory writes, ignores zero-length writes, and chooses cached versus non-cached handling.
- `FspFsvolWriteCached`:
  - Acquires the file node main resource.
  - Performs async oplock checks and byte-range lock checks.
  - Computes write-to-EOF and extension state.
  - Initializes the cache map when needed.
  - Defers through `CcDeferWrite` and WinFsp work items when cache manager throttling requires it.
  - Extends the file by issuing a set-information IRP before writing past EOF.
  - Performs copy writes or MDL writes through WinFsp cache-manager wrappers.
  - Updates synchronous current offset and marks the file modified.
- `FspFsvolWriteNonCached`:
  - Rejects MDL writes and invalid paging write-to-EOF cases.
  - Locks the user buffer for read access.
  - Acquires the file node full resource.
  - Performs oplock and file-lock checks for non-paging writes.
  - Flushes and purges cache when non-cached writes target a cached file.
  - Creates or resets a transact write request and fills user contexts, offset, length, key, and constrained-I/O state.
  - Sets request ownership on the file node and returns `FSP_STATUS_IOQ_POST`.
- `FspFsvolWritePrepare` maps write data for user-mode consumption, choosing either a copied process buffer or a safe MDL mapped into user mode.
- `FspFsvolWriteComplete` validates response length, updates file info, sends size-change notifications, updates synchronous offsets, marks modified state, resets the request, and reports bytes written.
- `FspFsvolWriteNonCachedRequestFini` releases process buffers or unmaps user-mode MDL mappings, dereferences captured process objects, deletes safe MDLs, and releases file-node ownership.
- `FspWrite` dispatches write IRPs only for fsvol devices.

Important dependencies:
- Cache-manager wrappers: `FspCcCopyWrite`, `FspCcPrepareMdlWrite`, `FspCcMdlWriteComplete`, `FspCcInitializeCacheMap`.
- File-node locking, oplock, cache flush/purge, owner, file-info, and notification helpers.
- `FspWqRepostIrpWorkItem` / `FspWqCreateIrpWorkItem` for retrying in waitable contexts.
- `FspIopCreateRequestEx`, `FspIopResetRequest`, and request context slots for non-cached transaction state.
- Safe-MDL and process-buffer helpers for exposing write data safely to user mode.
- WinFsp statistics counters for paging and non-cached write accounting.

Filesystem relevance:
- This is the write data path from Windows IRPs into a user-mode WinFsp filesystem.
- Cached writes may complete in-kernel through the cache manager when possible.
- Non-cached and paging writes are converted into `FspFsctlTransactWriteKind` requests for user-mode servicing.
- The file carefully separates normal writes, paging I/O, cache-extension behavior, MDL write paths, file-lock enforcement, and file-size/file-info updates.

Notable watchpoints:
- Fast I/O is deliberately denied for extending writes and write-to-EOF writes.
- Cached extension requires `CanWait`; otherwise the IRP is reposted to a work item.
- Non-cached writes on cached files force flush/purge before handing data to user mode.
- Paging writes are marked as constrained I/O and bypass normal oplock/file-lock checks.
- `FspFsvolWritePrepare` has two ownership modes encoded in the same context slot: copied process buffer with a tagged cookie, or safe-MDL mapping.
- Completion treats user-mode `Information` larger than requested length as `STATUS_INTERNAL_ERROR`.
