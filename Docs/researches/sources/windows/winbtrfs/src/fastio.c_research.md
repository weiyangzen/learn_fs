# File Research: sources/windows/winbtrfs/src/fastio.c

## Scope

This file initializes and implements the Windows `FAST_IO_DISPATCH` callbacks for WinBtrfs. It covers fast metadata queries, fast read/write dispatch integration, byte-range locking callbacks, cache manager section/flush callbacks, and resource acquisition ordering around copy-on-write filesystem state.

The file is in subset A through `sources/windows/winbtrfs`.

## High-Level Role

`fastio.c` is the fast-path bridge between the Windows I/O manager/cache manager and WinBtrfs FCB/CCB state. It answers simple file information queries without building full IRPs when safe, delegates cached reads and writes to FsRtl helpers, implements fast byte-range lock and unlock operations, and supplies the resource callbacks the cache manager needs for modified writes, cache flushes, and memory-mapped section creation.

## Main APIs And Entry Points

- `init_fast_io_dispatch(FAST_IO_DISPATCH** fiod)`: zeroes the global dispatch table, fills supported Fast I/O callbacks, and returns the table pointer to driver initialization code.
- `fast_query_basic_info(...)`: implements `FastIoQueryBasicInfo`, returning timestamps and attributes.
- `fast_query_standard_info(...)`: implements `FastIoQueryStandardInfo`, returning allocation size, EOF, link count, directory status, and delete-pending status.
- `fast_io_check_if_possible(...)`: checks byte-range locks and readonly/subvolume constraints for fast read/write eligibility.
- `fast_io_query_network_open_info(...)`: returns network-open information, including timestamps, allocation size, EOF, and attributes.
- `fast_io_acquire_for_mod_write(...)` / `fast_io_release_for_mod_write(...)`: acquire and release resources for cache manager modified-page writes.
- `fast_io_acquire_for_ccflush(...)` / `fast_io_release_for_ccflush(...)`: mark and unmark `FSRTL_CACHE_TOP_LEVEL_IRP` during cache flush callbacks.
- `fast_io_write(...)`: wraps `FsRtlCopyWrite` under the tree lock and updates inode size when the fast write succeeds.
- `fast_io_lock(...)`, `fast_io_unlock_single(...)`, `fast_io_unlock_all(...)`, `fast_io_unlock_all_by_key(...)`: route byte-range lock operations through FsRtl and refresh `Header.IsFastIoPossible`.
- `fast_io_acquire_for_create_section(...)` / `fast_io_release_for_create_section(...)`: acquire and release tree and FCB resources around section creation.

## Dispatch Table Contents

`init_fast_io_dispatch` installs:
- Custom callbacks for check-if-possible, write, basic info, standard info, locks/unlocks, network-open info, modified-write acquire/release, cache-flush acquire/release, and create-section acquire/release.
- FsRtl-provided helpers for cached fast reads and MDL reads/writes: `FsRtlCopyRead`, `FsRtlMdlReadDev`, `FsRtlMdlReadCompleteDev`, `FsRtlPrepareMdlWriteDev`, and `FsRtlMdlWriteCompleteDev`.

Unsupported Fast I/O entries remain zero because the table is cleared before assignment.

## Control Flow And Locking

Fast query paths enter the filesystem with `FsRtlEnterFileSystem`, validate `FileObject`, `FsContext`, and usually `FsContext2`, then acquire the relevant FCB resource shared if the caller permits waiting. Alternate data streams are mapped back to the parent file where Windows-visible timestamps, attributes, link counts, or delete-pending state must reflect the owning file rather than the ADS pseudo-FCB.

Fast write takes `Vcb->tree_lock` shared before calling `FsRtlCopyWrite`. On success it copies the cache manager file size back into `fcb->inode_item.st_size`, keeping in-memory inode metadata aligned with the cached write path.

Modified-page write acquisition deliberately takes `Vcb->tree_lock` shared before acquiring the FCB resource exclusive. The comment explains that this avoids interruption by the flush thread and uses the main FCB resource rather than `PagingIoResource` because Btrfs copy-on-write can require reallocations during writeback.

Section creation acquisition uses the same broad ordering: tree lock shared, then FCB resource exclusive. The release callback releases those resources in reverse order.

Byte-range lock and unlock callbacks only operate on regular files (`BTRFS_TYPE_FILE`). Locking acquires the FCB resource shared, calls the corresponding FsRtl fast lock/unlock helper, then recalculates `fcb->Header.IsFastIoPossible` through `fast_io_possible(fcb)`.

Cache flush callbacks use `IoSetTopLevelIrp((PIRP)FSRTL_CACHE_TOP_LEVEL_IRP)` and clear it only if the current top-level IRP is still that sentinel.

## Important State Read Or Mutated

- `FileObject->FsContext` as `fcb` and `FileObject->FsContext2` as `ccb`.
- `fcb->Header.Resource`, `fcb->Header.FileSize`, `fcb->Header.IsFastIoPossible`.
- `fcb->Vcb->tree_lock`, `fcb->Vcb->readonly`, `fcb->Vcb->dummy_fcb`, and `fcb->Vcb->volume_fcb`.
- `fcb->inode_item` timestamps, mode, size, link count, and object time.
- `fcb->atts`, `fcb->ads`, and `fcb->adsdata.Length`.
- `ccb->access` and `ccb->fileref`, including parent FCB and `delete_on_close`.
- `fcb->lock`, the FsRtl file-lock structure.
- Global `FastIoDispatch`.

## Dependencies

Windows kernel and FsRtl APIs used here include:
- `FAST_IO_DISPATCH` callback contracts and `_Function_class_` annotations.
- `FsRtlEnterFileSystem`, `FsRtlExitFileSystem`, `FsRtlCopyRead`, `FsRtlCopyWrite`, `FsRtlFastCheckLockForRead`, `FsRtlFastCheckLockForWrite`, `FsRtlFastLock`, `FsRtlFastUnlockSingle`, `FsRtlFastUnlockAll`, `FsRtlFastUnlockAllByKey`, and MDL helpers.
- `ExAcquireResourceSharedLite`, `ExAcquireResourceExclusiveLite`, and `ExReleaseResourceLite`.
- `IoSetTopLevelIrp`, `IoGetTopLevelIrp`, `KeQuerySystemTime`, and `PsGetCurrentProcess`.

Project-local dependencies include `btrfs_drv.h` types and helpers such as `fcb`, `ccb`, `file_ref`, `INODE_ITEM`, `unix_time_to_win`, `fcb_alloc_size`, `is_subvol_readonly`, `fast_io_possible`, `S_ISDIR`, and Btrfs file type constants.

## Notable Behaviors

- `fast_query_basic_info` enforces `FILE_READ_ATTRIBUTES` or `FILE_WRITE_ATTRIBUTES` access before answering.
- Dummy FCBs synthesize all timestamps from the current system time.
- Alternate data streams use their own stream length for allocation/EOF but derive attributes, link counts, and timestamps from the parent file where appropriate.
- `fast_io_query_network_open_info` zeroes the output structure first and does not acquire the FCB resource, so it is a very lightweight information path compared with the basic and standard query callbacks.
- Fast writes are blocked by inability to acquire the shared tree lock with the requested wait behavior.
- Fast write eligibility rejects writes on readonly volumes and readonly subvolumes before calling `FsRtlFastCheckLockForWrite`.
- Non-file lock requests are completed in the fast path with `STATUS_INVALID_PARAMETER` instead of falling back to IRP processing.

## Risks And Edge Cases

- `fast_query_standard_info` dereferences `ccb` for `ccb->fileref` near the end without first validating `ccb` in the non-ADS path. If a file object has an FCB but no CCB, this can fault.
- `fast_io_check_if_possible` assumes `FileObject` and `FileObject->FsContext` are valid and does not enter the filesystem or acquire resources. That matches a lightweight Fast I/O check style but relies on caller invariants and stable FCB lifetime.
- `fast_io_query_network_open_info` ignores `Wait` and does not lock the FCB resource while reading inode fields, ADS state, parent attributes, and sizes. Results can be stale or racing with metadata updates.
- In `fast_io_query_network_open_info`, `IoStatus` is marked unused with a FIXME asking whether `IoStatus->Information` should be set; successful fast query completion does not populate it here.
- `fast_io_write` does not validate file type, readonly state, or subvolume readonly state itself. It relies on Fast I/O eligibility and cache manager/FsRtl behavior to route only valid writes.
- The modified-write acquire path returns only the FCB resource in `ResourceToRelease`, but it also holds `tree_lock`; the paired release callback depends on recovering the FCB from `FileObject` to release both locks.
- Create-section acquisition takes the FCB resource exclusive, which is conservative and COW-friendly but can reduce concurrency for memory-mapped operations.
- Several callbacks return `false` on validation or lock acquisition failure, correctly forcing fallback to the normal IRP path, but any caller that expects `IoStatus` to be meaningful on those false returns will not get a populated status from most paths.

## Cross-File Relationships

- The dispatch pointer returned by `init_fast_io_dispatch` is used by the driver/device initialization path.
- The FCB, CCB, file-reference, and VCB fields used here are defined in `btrfs_drv.h` and maintained by create, cleanup, write, flush, and metadata paths elsewhere in WinBtrfs.
- `fast_io_write` interacts with later flush/extent code by updating `inode_item.st_size`; dirtying and extent allocation are handled by the broader write/cache-manager pipeline.
- The tree-lock ordering is coordinated with the flush thread and transaction code in `flushthread.c`.

## Summary

`fastio.c` provides WinBtrfs' Windows Fast I/O surface. It accelerates common metadata queries, cached reads/writes, byte-range locks, MDL operations, and cache manager resource callbacks while respecting the driver's tree lock and FCB resources. The file is intentionally thin, but its locking order and assumptions are important because these callbacks run in high-frequency kernel fast paths and interact with copy-on-write transaction flushing.
