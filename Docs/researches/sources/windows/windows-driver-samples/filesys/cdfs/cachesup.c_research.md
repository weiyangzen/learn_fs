# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cachesup.c

## Purpose

`cachesup.c` implements CDFS cache-manager support: creating/deleting internal stream file objects, completing MDL reads, and purging cached sections during lock/dismount paths.

## Main Routines

- `CdCreateInternalStream`
  - Creates an internal stream file object with `IoCreateStreamFileObjectLite`.
  - Attaches it to the FCB section object pointers.
  - Marks it read-only and identifies it as `StreamFileOpen`.
  - References the FCB to keep it alive while the stream object exists.
  - Initializes the cache map with `CcInitializeCacheMap` and `CdData.CacheManagerCallbacks`.
  - Stores the stream file in `Fcb->FileObject`.
  - For uninitialized directory FCBs, reads the self dirent, verifies it is `"."`, updates file/allocation/valid-data sizes, resets allocation mapping, imports hidden attribute/time fields, and marks `FCB_STATE_INITIALIZED`.
  - If sizes changed, purges stale cached pages.

- `CdDeleteInternalStream`
  - Removes `Fcb->FileObject` under the FCB lock.
  - Uninitializes the cache map when present.
  - Clears `FileName` pointers because the stream file only borrows FCB-owned name buffers.
  - Dereferences the file object.

- `CdCompleteMdl`
  - Completes MDL read cleanup via `CcMdlReadComplete`.
  - Clears `Irp->MdlAddress`.
  - Completes the IRP with `STATUS_SUCCESS`.

- `CdPurgeVolume`
  - Flushes delayed closes with `CdFspClose`.
  - Acquires the global file resource to block file operations.
  - Iterates all FCBs in the VCB FCB table, references each while processing, flushes image sections, purges data cache sections, and tears down eligible structures.
  - On dismount, deletes internal streams for directory/path-table FCBs.
  - Also purges/deletes path table and volume DASD FCB state when `DismountUnderway` is true.
  - Returns the first `STATUS_UNABLE_TO_DELETE_SECTION` if cache purge fails because a section remains mapped.

## Important Behavior

Internal stream files are central to cached reads of directories and path tables. They borrow FCB names for profiling/debugging, so teardown must null those names before object dereference.

Directory stream initialization is tied to the self entry. If the on-disc self dirent is missing, has zero aligned length, or does not parse as the expected self name, the code raises corruption.

## Integration

This module interacts with the Windows Cache Manager (`CcInitializeCacheMap`, `CcSetFileSizes`, `CcPurgeCacheSection`, `CcUninitializeCacheMap`), Memory Manager image-section flushing, FCB reference accounting, allocation support (`CdTruncateAllocation`, `CdAddInitialAllocation`), dirent support, and volume teardown.

## Risk Notes

- Stream-file lifetime depends on exact reference-count pairing. `CdCreateInternalStream` intentionally takes two references and unwinds one on failure.
- Cache purge during dismount can fail when image/data sections remain mapped, returning `STATUS_UNABLE_TO_DELETE_SECTION`.
- The self-dirent validation protects directory stream sizing; corrupted media can force cleanup through exception paths.
