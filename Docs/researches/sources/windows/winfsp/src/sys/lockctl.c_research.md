# File Research: sources/windows/winfsp/src/sys/lockctl.c

## Purpose

`lockctl.c` handles `IRP_MJ_LOCK_CONTROL` for WinFsp filesystem volume devices. It validates the target file, performs oplock checks, and delegates byte-range lock processing to the FsRtl file-lock package through WinFsp file-node helpers.

## Main Contents

- `FspFsvolLockControlRetry` is the main retryable lock path.
- `FspFsvolLockControl` validates the request and starts the retry path.
- `FspFsvolLockControlComplete` is an I/O completion logging stub using WinFsp's completion macros.
- `FspLockControl` dispatches by device extension kind.

## Control Flow

1. `FspLockControl` accepts only `FspFsvolDeviceExtensionKind`.
2. `FspFsvolLockControl` rejects invalid file nodes and directories.
3. `FspFsvolLockControlRetry` tries to acquire the file node main resource shared.
4. If acquisition fails, it reposts the IRP as a work item.
5. It performs `FspFileNodeOplockCheckAsync`.
6. If the oplock check succeeds, it clears the top-level IRP and calls `FspFileNodeProcessLockIrp`.
7. It releases the file node based on saved IRP flags and returns the result with `FSP_STATUS_IGNORE_BIT`.

## Integration

The file depends on `FSP_FILE_NODE` locking, oplock helpers, work-queue reposting, and FsRtl file-lock support wrapped by `FspFileNodeProcessLockIrp`.

## Notable Details

- Lock control is accepted only for regular files.
- Asynchronous oplock checks may return `STATUS_PENDING`.
- `FSP_STATUS_IGNORE_BIT` indicates the IRP has been handled in a way that normal dispatch completion should ignore.
