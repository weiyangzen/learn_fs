# File Research: sources/windows/windows-driver-samples/filesys/fastfat/cachesup.c

## Purpose

Implements FastFAT cache-manager integration for volume FAT data, directory stream files, EA stream files, dirty/repinned BCB handling, MDL completion, synchronous cache-map teardown, mapped-data pinning, zeroing, and Win8+ page prefetch.

## Key routines

- `FatInitializeCacheMap`: wrapper for `CcInitializeCacheMap`; enables disk I/O accounting on Win8+ when configured.
- `FatReadVolumeFile`: maps FAT volume-file ranges through `CcMapData`.
- `FatPrepareWriteVolumeFile`: pins FAT volume-file ranges with `CcPinRead`, optionally zeroes them, and marks dirty through `FatSetDirtyBcb`.
- `FatReadDirectoryFile`: opens/initializes a directory stream file if needed and maps or pins directory data.
- `FatPrepareWriteDirectoryFile`: extends directory allocation when needed, pins pages or VACB-sized ranges, zeroes new allocation, and marks data dirty.
- `FatOpenDirectoryFile`: creates and initializes the internal stream file object for a directory.
- `FatOpenEaFile` / `FatCloseEaFile`: create and tear down the EA stream file and cache map.
- `FatSetDirtyBcb`: optionally repins a BCB, marks it dirty, and manages delayed volume-clean/dirty state.
- `FatRepinBcb`: stores unique BCB references in the IRP context for later controlled unpin.
- `FatUnpinRepinnedBcbs`: write-through unpins repinned BCBs, purges cache sections on selected removable-media failures, and raises failed flush status unless disabled.
- `FatZeroData`: sector-aligns and delegates zeroing to `CcZeroData`.
- `FatCompleteMdl`: completes MDL read/write requests through cache-manager MDL completion APIs.
- `FatSyncUninitializeCacheMap`: synchronously waits for `CcUninitializeCacheMap` completion.
- `FatPinMappedData`: pins already mapped directory data.
- `FatPrefetchPages`: Win8+ helper that builds an `MM_PREFETCH` read list and calls `MmPrefetchPages`.

## Directory cache flow

Directory reads and writes call `FatOpenDirectoryFile` to ensure a stream file object and cache map exist. If allocation size is unknown, the code resolves it through `FatLookupFileAllocationSize`, sets directory file size from allocation size, and checks the free-dirent bitmap.

`FatPrepareWriteDirectoryFile` grows directory allocation with `FatAddFileAllocation` if the write extends beyond current allocation. FAT12/16 root directories cannot grow and return disk full. After growth, it updates cache-manager file sizes and zeroes newly allocated clusters. It pins in page-sized chunks within the original request to avoid OBCBs, then uses `VACB_MAPPING_GRANULARITY` after crossing the original request boundary for efficiency. On abnormal termination after allocation growth, it truncates back to the original allocation and updates cache sizes.

## Dirty and repinned BCB handling

`FatSetDirtyBcb` calls `CcSetDirtyPinnedData`, and when allowed marks the volume dirty for non-FAT12 volumes. It throttles physical dirty marking/timer updates to roughly once per second, sets a clean-volume timer, and disables eject for removable media when transitioning dirty.

`FatRepinBcb` records each BCB once in a linked list of `REPINNED_BCBS` arrays stored from the IRP context. `FatUnpinRepinnedBcbs` later unpins all of them, optionally write-through for write-through or deferred-flush media. On failures for removable/deferred-flush media, it can unpin other BCBs from the same file, purge the file cache section, force verify, and propagate normalized status.

## Internal stream files

`FatOpenDirectoryFile` creates an internal stream file object with `IoCreateStreamFileObject`, associates it with the DCB, increments internal/residual open counts, assigns section object pointers, grants access flags, and initializes a cache map using no-op callbacks.

`FatOpenEaFile` performs analogous setup for the EA file, but uses `FatData.CacheManagerCallbacks` and calls `CcSetAdditionalCacheAttributes` to disable read-ahead/write-behind-style behavior for EA handling. `FatCloseEaFile` flushes optionally, clears `Vcb->VirtualEaFile`, clears the EA MCB, synchronously uninitializes the cache map, and dereferences the stream file object.

## Synchronization and debug checks

In debug builds, `FatIsCurrentOperationSynchedForDcbTeardown` validates that a directory open operation is protected against DCB teardown by mount state, VCB ownership, parent-by-child context, or an operation file object rooted under the DCB. `FatOpenDirectoryFile` asserts this before adding an internal open.

Directory stream creation uses a directory-file mutex and double-checks `Dcb->Specific.Dcb.DirectoryFile` under that mutex.

## Dependencies

Depends on `FatProcs.h`, allocation support (`FatAddFileAllocation`, `FatTruncateFileAllocation`, `FatLookupFileAllocationSize`), directory bitmap support, close-context preallocation, FastFAT file-object tagging, cache manager APIs, memory manager prefetch APIs for Win8+, and kernel synchronization/timer/DPC primitives.

## Edge cases and notes

- `FatReadVolumeFile` asserts reads stay within the boot/reserved/FAT region, with a mount-time exception for offset zero.
- `FatPrepareWriteVolumeFile` ensures pinned data is unpinned on abnormal termination.
- `FatZeroData` returns success for sector-fragment-only zero requests because `CcZeroData` cannot handle non-sector-aligned ranges in this temporary helper.
- `FatCompleteMdl` only accepts read and write major functions; any other major function bugchecks.
- `FatPrefetchPages` treats zero-page prefetch as success and frees its read list on all exit paths.
