# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/rw.c

## Purpose

`rw.c` implements VFAT read/write handling, including cluster-chain translation, cached I/O through the cache manager, noncached/raw disk I/O, page-file forwarding, byte-range lock checks, stack-overflow read posting, file extension, write metadata updates, and I/O statistics.

## Cluster Helpers

- `NextCluster()` returns the next logical cluster. FAT12/16 root-directory sentinel cluster `1` advances by sectors-per-cluster; other chains call either normal or extending FAT callbacks.
- `OffsetToCluster()` converts a file offset to a cluster number by walking from the first cluster. It also handles FAT12/16 root-directory cluster `1` by mapping directly into the root directory's fixed sector range.

## Low-Level Read/Write Data Paths

- `VfatReadFileData()`:
  - Handles FAT stream reads by adding `FATStart`.
  - Handles volume reads as raw disk reads.
  - Handles FAT12/16 root-directory reads as fixed root-area reads.
  - For normal files, uses the FCB last-cluster/last-offset cache when possible, groups contiguous clusters into larger disk reads, uses `VfatReadDiskPartial()`, and waits for outstanding partial reads through the IRP-context event/refcount.
- `VfatWriteFileData()`:
  - Handles volume writes directly.
  - Writes FAT stream data to every FAT copy.
  - Handles FAT12/16 root-directory writes directly into the fixed root area.
  - Groups contiguous clusters for normal file writes and submits partial disk writes.

## Read Dispatch

- `VfatRead()` rejects reads on the global filesystem device and non-paging directory reads.
- Page-file reads are converted to storage-device offsets and forwarded directly down the stack.
- Non-volume high 32-bit offsets are rejected, reflecting this driver's 32-bit file-size assumptions.
- Zero-length reads succeed; reads beyond EOF return `STATUS_END_OF_FILE`.
- Noncached, paging, and volume reads must be sector aligned.
- Resource choice:
  - volume: `DirResource`
  - paging I/O: FCB `PagingIoResource`
  - normal read: FCB `MainResource`
- If remaining kernel stack is low, it locks the user buffer and posts through `FsRtlPostStackOverflow()` or `FsRtlPostPagingFileStackOverflow()`.
- `VfatCommonRead()` performs lock checks, cached `CcCopyRead()` for normal cached file reads, or noncached `VfatReadFileData()` after MDL locking.

## Write Dispatch

- `VfatWrite()` rejects the global filesystem device and non-paging directory writes.
- Page-file writes are offset-adjusted and forwarded directly to the storage device.
- `FILE_WRITE_TO_END_OF_FILE` is resolved to the current file size.
- FAT stream, volume stream, and FAT12/16 root-directory writes cannot extend beyond current file size.
- Noncached, paging, and volume writes must be sector aligned.
- Cache-manager throttling uses `CcCanIWrite()` and `CcDeferWrite()`; deferred writes hand ownership of the IRP context to the cache-manager callback.
- Resource choice mirrors reads, but non-paging normal writes acquire the main resource exclusively.
- If a cached/non-paging normal write extends the file, `VfatSetAllocationSizeInformation()` is called under `DirResource`.
- Cached writes initialize the cache map if needed, zero gaps with `CcZeroData()`, and call `CcCopyWrite()`.
- Noncached writes lock the user buffer and call `VfatWriteFileData()`.
- Successful non-paging, non-FAT, non-volume file writes update DOS timestamps, mark the FCB dirty, and report notifications for last-write/attribute and size changes.

## Important Details

- The last-cluster cache is protected by `Fcb->LastMutex` and accelerates sequential I/O.
- The code has an optional `DEBUG_VERIFY_OFFSET_CACHING` path that recomputes cluster positions and bugchecks on cache mismatch.
- Noncached I/O rounds read limits to sector-rounded file sizes.
- Synchronous file objects have `CurrentByteOffset` advanced on successful read/write completion.

## Research Notes

This file is the main place to study data-path correctness. Important edge cases include FAT copy writes, EOF/sector rounding, file-extension ordering, cached/noncached coherence, and the direct page-file bypass.
