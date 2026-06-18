# File Research: sources/os/linux/linux/fs/f2fs/file.c

Read completely: 5491 lines.

## Summary
Implements F2FS VFS-facing regular-file behavior: mmap faults, page-mkwrite, fsync, llseek, open/release/flush, truncate, fallocate, file attributes, ioctl dispatch, direct and buffered read/write paths, splice read, fadvise, atomic-write controls, compression controls, device trim, GC/checkpoint user ioctls, and shutdown handling.

## Main Responsibilities
- Provides `f2fs_file_operations` and `f2fs_file_inode_operations`.
- Handles roll-forward-safe fsync and checkpoint fallback decisions.
- Implements truncation, hole punching, zero/collapse/insert range, preallocation, and block-range movement.
- Exposes F2FS-specific ioctls for atomic writes, GC, defrag, move range, flush device, resize, pinning, compression, verity, encryption, secure trim, and labels.
- Chooses between buffered I/O and iomap direct I/O.
- Maintains file flags, project quota, pin-file state, direct-I/O alignment reporting, and extent precaching.
- Coordinates with compression, encryption, verity, quota, checkpoint, GC, multi-device, zoned, and atomic-write subsystems.

## Key APIs
- Operations tables: `f2fs_file_operations`, `f2fs_file_inode_operations`, `f2fs_file_vm_ops`.
- Sync/mmap/open: `f2fs_sync_file()`, `f2fs_file_mmap_prepare()`, `f2fs_file_open()`, `f2fs_release_file()`, `f2fs_file_flush()`.
- Truncate/fallocate: `f2fs_truncate()`, `f2fs_truncate_blocks()`, `f2fs_truncate_hole()`, `f2fs_fallocate()`.
- Ioctl dispatch: `f2fs_ioctl()`, `f2fs_compat_ioctl()`, `__f2fs_ioctl()`.
- Atomic writes: `f2fs_ioc_start_atomic_write()`, `f2fs_ioc_commit_atomic_write()`, `f2fs_ioc_abort_atomic_write()`.
- Data I/O: `f2fs_file_read_iter()`, `f2fs_file_write_iter()`, `f2fs_dio_read_iter()`, `f2fs_dio_write_iter()`.
- Admin/control helpers: `f2fs_do_shutdown()`, `f2fs_precache_extents()`, `f2fs_pin_file_control()`.

## Important Behavior
`f2fs_do_sync_file()` first writes dirty data, then decides whether the file can be recovered by roll-forward node logging or needs a full checkpoint. Checkpoint is forced for non-regular files, compressed files, hardlinks, wrong parent inode tracking, low roll-forward space, strict fsync directory recovery, fastboot, and other global conditions.

`f2fs_vm_page_mkwrite()` converts inline data, allocates or verifies a backing block, waits for writeback and GC writeback, zeroes EOF fragments, and marks the folio dirty. Large folios are explicitly rejected for write faults.

Truncation clears dnode block addresses, invalidates physical blocks, updates read and age extent caches, handles compressed cluster alignment, clears partial EOF data, and converts inline data when the new size no longer fits inline storage.

Fallocate supports punch hole, collapse range, zero range, insert range, and preallocation. Pinned and compressed files reject partial range transforms. Pinned-file expansion allocates section-aligned pinned blocks and may trigger foreground GC.

Block exchange helpers power collapse/insert/move/defrag paths. They read source block addresses, optionally replace uncheckpointed blocks, clone or copy data, roll back partial failures, and update inode size.

The ioctl table is broad. It includes atomic write lifecycle, shutdown modes, FITRIM, fscrypt policy/key calls, GC and GC range, checkpoint write, defragment, move range, flush device, feature query, pin-file controls, extent precache, resize, fs-verity, filesystem label, compression block release/reserve, secure trim, compression options, user-triggered compress/decompress, device-alias query, and I/O priority hints.

Direct I/O is disabled or falls back to buffered I/O for unsupported fscrypt DIO, verity, compression, inline reads, unaligned multi-device layouts, non-pinned zoned writes, checkpoint-disabled mode, and compatible misalignment cases. Partial direct writes fall back to buffered writes and flush/drop page cache to preserve O_DIRECT semantics.

## State and Synchronization
Uses inode locks, `i_gc_rwsem[READ/WRITE]`, `f2fs_lock_op()`, filemap invalidate locks, folio locks, `pin_sem`, `gc_lock`, `sb_lock`, quota transfers under operation locking, writeback counters, and atomic/COW inode references. Many paths wait for direct I/O, data writeback, node writeback, or block writeback before moving or invalidating blocks.

## Risks
This file is the main policy junction for user-visible file behavior. Lock ordering across inode locks, filemap invalidate locks, `i_gc_rwsem`, `gc_lock`, and `f2fs_lock_op()` is critical. Range transforms and move operations are vulnerable to partial failure, stale block-address validation, and rollback mistakes. Compression release/reserve and user-triggered compress/decompress can leave partially transformed files and intentionally mark the filesystem for fsck in some failure cases. Direct-I/O fallback must preserve O_DIRECT semantics while still allowing legacy buffered fallback behavior.
