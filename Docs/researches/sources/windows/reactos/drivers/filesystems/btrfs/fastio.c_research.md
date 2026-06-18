# File Research: sources/windows/reactos/drivers/filesystems/btrfs/fastio.c

## Purpose

Defines and initializes the Windows `FAST_IO_DISPATCH` table for the ReactOS/WinBtrfs filesystem driver. The file provides fast-path handlers for metadata queries, cached read/write integration, byte-range locking, memory-manager section synchronization, modified-page-writer synchronization, and cache flush top-level IRP handling.

## Main Responsibilities

- Populate the global `FastIoDispatch` structure used by the driver object.
- Provide fast query paths for basic, standard, and network-open file information.
- Route cached reads directly to `FsRtlCopyRead`.
- Wrap cached writes with Btrfs tree-lock handling and update FCB file size state.
- Validate fast I/O feasibility against byte-range locks and readonly state.
- Expose fast lock/unlock handlers through FsRtl lock helpers.
- Coordinate resource acquisition for section creation, modified writes, and cache flushes.

## Key Functions

- `fast_query_basic_info`: Returns timestamps and attributes using FCB inode metadata; redirects alternate data streams to the parent file’s FCB.
- `fast_query_standard_info`: Returns allocation size, EOF, link count, directory flag, and delete-pending state; handles alternate data stream sizes separately.
- `fast_io_check_if_possible`: Uses FsRtl byte-range lock checks for reads and writes; rejects writes on readonly volumes or readonly subvolumes.
- `fast_io_query_network_open_info`: Fills `FILE_NETWORK_OPEN_INFORMATION` for normal files, dummy FCBs, and alternate data streams.
- `fast_io_acquire_for_mod_write`: Acquires `Vcb->tree_lock` shared and the FCB resource exclusive for modified-page-writer operations.
- `fast_io_release_for_mod_write`: Releases the FCB resource and tree lock acquired by the modified-write callback.
- `fast_io_acquire_for_ccflush` / `fast_io_release_for_ccflush`: Mark and clear `FSRTL_CACHE_TOP_LEVEL_IRP` during cache-manager flush callbacks.
- `fast_io_write`: Acquires the tree lock, calls `FsRtlCopyWrite`, and updates `fcb->inode_item.st_size` after successful cached writes.
- `fast_io_lock`, `fast_io_unlock_single`, `fast_io_unlock_all`, `fast_io_unlock_all_by_key`: Implement fast byte-range lock and unlock operations and refresh `Header.IsFastIoPossible`.
- `fast_io_acquire_for_create_section` / `fast_io_release_for_create_section`: Acquire/release tree and FCB resources for section creation.
- `init_fast_io_dispatch`: Zeroes and fills the `FAST_IO_DISPATCH` table.

## Dispatch Table

`init_fast_io_dispatch` installs handlers for:

- Fast I/O feasibility checks.
- Cached read/write.
- Query basic, standard, and network-open information.
- Lock/unlock operations.
- Section create acquire/release.
- Modified write acquire/release.
- MDL read/write callbacks via FsRtl helper functions.
- Cache flush acquire/release callbacks.

The dispatch table is assigned to the driver object from `btrfs.c`.

## Important Behavior

- Most query handlers enter the filesystem with `FsRtlEnterFileSystem` and leave with `FsRtlExitFileSystem`.
- Basic and standard info queries acquire the FCB resource shared, respecting the caller’s wait flag.
- Alternate data streams use the stream FCB for stream length but use the parent FCB for file metadata such as timestamps, attributes, and link count.
- `fast_io_write` uses a shared tree lock around `FsRtlCopyWrite`; this is important because Btrfs copy-on-write metadata updates can interact with cached writes.
- Modified-page-writer acquisition avoids waiting and returns `STATUS_CANT_WAIT` if either the tree lock or file resource cannot be acquired immediately.
- Byte-range locking is restricted to regular file FCBs; non-file objects return `STATUS_INVALID_PARAMETER` through `IoStatus`.
- ReactOS-specific `_Function_class_` annotations are applied around create-section acquire/release callbacks under `__REACTOS__`.

## Cross-File Interactions

- Uses FCB, CCB, file reference, inode, subvolume, and VCB structures from `btrfs_drv.h`.
- Calls helpers such as `unix_time_to_win`, `fcb_alloc_size`, `is_subvol_readonly`, and `fast_io_possible`.
- Byte-range locks operate on `fcb->lock`; successful lock state changes update `fcb->Header.IsFastIoPossible`.
- The global dispatch table is connected to the driver in `btrfs.c` through `init_fast_io_dispatch`.

## Edge Cases and Risks

- `fast_io_query_network_open_info` explicitly leaves `IoStatus` unused, with a FIXME questioning whether `IoStatus->Information` should be set.
- Some callbacks assume `FileObject->FsContext` is valid after entry, especially lock/write paths, so callers must only route suitable objects through these fast paths.
- `fast_query_standard_info` uses `ccb` for delete-pending state after only validating `fcb` before resource acquisition; normal fast I/O invocation should provide a CCB, but malformed state would be risky.
- The create-section and modified-write paths acquire resources in a fixed tree-lock then FCB-resource order, matching the driver’s COW synchronization expectations.

## Research Summary

This file is the Btrfs driver’s Windows Fast I/O integration layer. It does not implement filesystem allocation or metadata updates itself, but it determines when cached I/O, metadata queries, lock operations, section creation, and cache flushes can take the fast path while preserving the driver’s resource locking rules.
