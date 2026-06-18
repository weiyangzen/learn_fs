# File Research: sources/windows/reactos/drivers/filesystems/fastfat/cachesup.c

## Purpose

`cachesup.c` wraps Windows Cache Manager operations used by FastFAT for volume FAT access, directory-file access, EA-file access, dirty pinned BCB tracking, repinned BCB writeback, zeroing, MDL completion, cache uninitialization, and optional page prefetching.

## Main Responsibilities

- Initialize cache maps with FastFAT callbacks and optional disk I/O accounting.
- Map or pin volume-file FAT/reserved-sector data.
- Map, pin, extend, and zero cached directory data.
- Create and cache internal stream file objects for directories and EA data.
- Mark BCBs dirty and schedule volume dirty/clean state transitions.
- Repin BCBs for reversible metadata operations and later unpin/write them through.
- Purge cache on write-through errors for removable/deferred-flush media.
- Provide MDL read/write completion helpers.
- Synchronize cache uninitialization for teardown.
- Prefetch FAT pages on supported NTDDI versions.

## Key Functions

`FatInitializeCacheMap`

- Calls `CcInitializeCacheMap`.
- On Windows 8+ builds, enables Cache Manager disk I/O accounting when `FatDiskAccountingEnabled` is set.

`FatReadVolumeFile`

- Maps bytes from the virtual volume file.
- Used for boot/reserved/FAT regions where VBO equals LBO.
- Asserts accesses remain within the BPB/FAT area, with a mount-time exception for offset zero.
- Raises `STATUS_CANT_WAIT` if nonblocking cache mapping would block.

`FatPrepareWriteVolumeFile`

- Pins volume-file bytes for metadata writes.
- Optionally zeroes the pinned buffer.
- Marks the BCB dirty through `FatSetDirtyBcb`, optionally reversible.
- Unpins on abnormal termination.

`FatReadDirectoryFile`

- Ensures a directory stream file object and cache map exist via `FatOpenDirectoryFile`.
- Handles zero-byte reads and EOF.
- Truncates reads at allocation size.
- Uses either `CcPinRead` or `CcMapData` depending on the caller's `Pin` argument.
- Raises `STATUS_CANT_WAIT` for nonblocking cache misses.

`FatPrepareWriteDirectoryFile`

- Ensures directory cache state exists.
- Extends directory allocation if the write exceeds current allocation, except non-FAT32 root directories which cannot grow.
- Updates cache-manager sizes after extension.
- Ensures the free-dirent bitmap is large enough.
- Pins in page-sized chunks inside the original request, then can use `VACB_MAPPING_GRANULARITY` chunks beyond it to avoid OBCB/repin problems.
- Zeroes newly allocated directory clusters and dirties them.
- On failure, unpins buffers and truncates back to the initial allocation when this routine allocated new disk space.

`FatIsCurrentOperationSynchedForDcbTeardown` debug-only

- Verifies the current operation has enough synchronization to safely attach an internal directory file object to a DCB.
- Accepts mount operations, held VCB resources, parent-by-child contexts, or file objects that refer to the DCB or descendants.
- Can be bypassed by `FatDisableParentCheck` in debug builds.

`FatOpenDirectoryFile`

- Resolves unknown allocation size if necessary.
- Ensures the directory free-dirent bitmap exists.
- Lazily creates an internal stream file object under the directory-file mutex.
- Sets FastFAT file object type to `DirectoryFile`, increments internal/residual opens, assigns section object pointers, and grants read/write/delete access.
- Initializes the directory cache map with no-op cache callbacks.
- Asserts synchronization against DCB teardown in debug builds.

`FatOpenEaFile`

- Creates an internal stream file object for EA data.
- Preallocates close context, sets file object type to `EaFile`, increments internal/residual opens, assigns section object pointers, and initializes cache map with normal FastFAT callbacks.
- Sets additional cache attributes for the EA stream.

`FatCloseEaFile`

- Requires exclusive VCB ownership.
- Optionally flushes the EA file cache.
- Clears `VirtualEaFile`, empties the EA FCB MCB, synchronously uninitializes the cache map, and dereferences the stream file object.

`FatSetDirtyBcb`

- Optionally repins the BCB for reversible metadata changes.
- Calls `CcSetDirtyPinnedData`.
- Unless dirty marking is disabled, marks non-FAT12 volumes dirty.
- Uses throttling based on `LastFatMarkVolumeDirtyCall`.
- Sets or refreshes a clean-volume timer: shorter for deferred-flush/hot-plug volumes, longer otherwise.
- If transitioning to dirty, writes physical dirty state through `FatMarkVolume`, sets `VCB_STATE_FLAG_VOLUME_DIRTY`, and disables eject for removable media.

`FatRepinBcb`

- Maintains a dense linked list of repinned BCB arrays inside `IrpContext`.
- Avoids duplicate repinning of the same BCB.
- Allocates additional `REPINNED_BCBS` records as needed.

`FatUnpinRepinnedBcbs`

- Walks all repinned BCBs and calls `CcUnpinRepinnedBcb`.
- Determines write-through behavior from request flags and deferred-flush media.
- Captures the first writeback error.
- For deferred-flush removable media write failures, may purge the affected file cache after unpinning other BCBs for the same file to avoid deadlock.
- Avoids purging for cleanup, flush, set-information, and a specific create/verify-required case where create rollback handles the state.
- Forces volume verify on serious write-through failures and raises normalized status unless raising is disabled.

`FatZeroData`

- Aligns zeroing to sector boundaries because this helper exists for non-sector-aligned limitations.
- Returns success for purely partial-sector ranges that require no whole-sector zeroing.
- Calls `CcZeroData` with the current wait policy.

`FatCompleteMdl`

- Completes MDL read or write requests.
- Uses `CcMdlReadComplete` for reads and `CcMdlWriteComplete` for writes.
- Clears `Irp->MdlAddress` and completes the IRP.
- Bugchecks on unsupported major functions.

`FatSyncUninitializeCacheMap`

- Calls `CcUninitializeCacheMap` with a completion event and waits for it.
- Used when teardown must know cache/Mm purge processing has completed.

`FatPinMappedData`

- Pins previously mapped directory data with `CcPinMappedData`.
- Raises `STATUS_CANT_WAIT` on nonblocking cache miss.

`FatPrefetchPages`

- Windows 8+ helper.
- Retrieves I/O priority from the originating IRP.
- Builds a `READ_LIST` and calls `MmPrefetchPages`.
- Caps behavior to nonzero page counts and frees the read list on cleanup.

## Dependencies and Interactions

- Depends on Cache Manager APIs: `CcInitializeCacheMap`, `CcMapData`, `CcPinRead`, `CcSetDirtyPinnedData`, `CcRepinBcb`, `CcUnpinRepinnedBcb`, `CcPurgeCacheSection`, `CcZeroData`, `CcMdlReadComplete`, `CcMdlWriteComplete`, and `CcUninitializeCacheMap`.
- Interacts closely with allocation support through `FatAddFileAllocation`, `FatTruncateFileAllocation`, `FatLookupFileAllocationSize`, and MCB manipulation.
- Uses FastFAT volume state and timers to coordinate dirty/clean volume transitions.
- Creates internal stream file objects with `IoCreateStreamFileObject`.
- Relies on section object pointers stored in FCB/DCB nonpaged state.

## Synchronization Model

- Directory stream file creation is protected by `FatAcquireDirectoryFileMutex` / `FatReleaseDirectoryFileMutex`.
- Several routines require the global critical region.
- `FatCloseEaFile` requires exclusive VCB ownership.
- Dirty volume timer state is guarded with `FatData.GeneralSpinLock`.
- Repinned BCB cleanup is serialized through the owning `IrpContext`.

## Error Handling and Recovery

- Cache miss without wait raises `STATUS_CANT_WAIT`.
- Directory extension failures unwind pinned BCBs and newly allocated disk space.
- EA file open dereferences the stream file object on abnormal termination.
- Repinned BCB write failures preserve the first error and may purge cache plus force verify.
- Synchronous cache uninitialization asserts successful wait completion.

## Important Edge Cases

- Non-FAT32 root directories cannot be extended.
- Directory write preparation pins page-granular chunks initially to avoid OBCBs that cannot be safely repinned.
- Partial-sector zeroing may intentionally be a no-op.
- FAT12 volumes are excluded from dirty-volume bit processing.
- Deferred-flush/removable media paths are stricter about write-through and verify handling.
