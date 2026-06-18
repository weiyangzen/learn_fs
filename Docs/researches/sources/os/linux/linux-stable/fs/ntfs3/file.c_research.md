# File Research: sources/os/linux/linux-stable/fs/ntfs3/file.c

## Summary
Implements the NTFS3 regular-file VFS surface: ioctls, getattr/setattr, mmap preparation, truncate/extend, fallocate, read/write/splice paths, compressed-file write handling, open/release, fiemap, fsync, llseek, and the exported inode/file operation tables.

## Main Responsibilities
- Provide regular-file `inode_operations` and `file_operations` for NTFS3.
- Dispatch NTFS3 ioctls for trim, filesystem label get/set, and forced shutdown.
- Enforce unsupported-feature restrictions for encrypted, deduplicated, compressed, immutable, and forced-shutdown files.
- Maintain NTFS file size and initialized-size semantics across truncate, extension, mmap write mappings, buffered I/O, direct I/O, and fallocate.
- Integrate with Linux iomap for buffered I/O, direct I/O, zeroing, fiemap, and page-cache backed writes.
- Handle native NTFS compressed write frames through `ni_read_frame()` and `ni_write_frame()`.
- Finalize delayed allocation and optional preallocation cleanup when the last writer closes a file.

## Key Interfaces
- `ntfs_ioctl()` and `ntfs_compat_ioctl()` implement `FITRIM`, `FS_IOC_GETFSLABEL`, `FS_IOC_SETFSLABEL`, and `NTFS3_IOC_SHUTDOWN`.
- `ntfs_getattr()` exposes NTFS birth time, cluster preferred block size, immutable/append/compressed/encrypted statx attributes.
- `ntfs_setattr()` handles size changes, chmod ACL updates, Windows readonly flag mirroring, and WSL permission persistence.
- `ntfs_fallocate()` implements punch-hole, collapse-range, insert-range, preallocation, sparse/compressed hole support, and keep-size handling.
- `ntfs_file_read_iter()`, `ntfs_file_write_iter()`, splice helpers, and mmap preparation form the main data I/O surface.
- `ntfs_file_fsync()` writes file data, inode metadata, parent directory duplicate info, MFT mirror updates, and block-device cache flushes.
- `ntfs_llseek()` supports `SEEK_DATA` and `SEEK_HOLE` through `ni_seek_data_or_hole()`.

## Important Behavior
Direct I/O is only attempted when `ntfs_dio_alignment()` returns a real block alignment and both file offset and iterator alignment satisfy it. Resident files without delayed allocation bypass DIO; files with delayed allocation force allocation before direct reads/writes because DIO cannot safely operate on delalloc runs.

Writes call `generic_write_checks()`, `file_modified()`, `ntfs_extend()`, and then either compressed-frame writing, buffered iomap writing, direct iomap writing, or a mixed DIO-to-buffered fallback. The fallback writes and invalidates page-cache pages to preserve direct-I/O semantics for the remainder of a partially completed request.

Initialized size is explicit NTFS state (`ni->i_valid`). `ntfs_extend_initialized_size()` zeroes the gap through iomap for nonresident files, while resident files can simply move `i_valid`. mmap write preparation allocates sparse clusters and extends initialized size up to the mapped writable range, installing custom VM ops so `close` can mark `i_valid` advanced after writable mappings.

Fallocate coordinates page-cache writeback/invalidation, DIO quiescing, inode locking, and NTFS attribute helpers. Punching an unaligned compressed/sparse frame zeroes head/tail pieces and deallocates only the aligned interior. Insert and collapse range are protected by invalidate locks and write out affected cache ranges before metadata movement.

Compressed writes operate one NTFS LZNT frame at a time. The code locks or creates all pages in a frame, reads existing frame data when partial updates require it, copies user data atomically, calls `ni_write_frame()` under `ni_lock()`, clears dirty state, unlocks pages, and updates file position, initialized size, and inode size.

## State and Synchronization
The file uses VFS inode locks, shared inode locks for DIO reads/fiemap/seek, `inode_dio_wait()` before range mutation, `filemap_invalidate_lock()` around hole/range operations, `ni_lock()`, and `ni->file.run_lock` for runlist/attribute size changes. It marks NTFS volume state dirty before mutating metadata and marks inodes dirty after size/time/attribute updates.

## Cross-File Interactions
Most metadata work is delegated to `attrib.c` helpers such as `attr_set_size_ex()`, `attr_data_get_block()`, `attr_punch_hole()`, `attr_collapse_range()`, `attr_insert_range()`, and `attr_force_nonresident()`. I/O mapping is delegated to `ntfs_iomap_ops` and `ntfs_iomap_folio_ops`. Compressed read/write frame mechanics and delayed allocation finalization come from `frecord.c` through `ni_read_frame()`, `ni_write_frame()`, and `ni_allocate_da_blocks()`.

## Risks
Correctness depends on preserving NTFS initialized-size semantics so reads beyond `i_valid` return zeroes and writes cannot expose stale disk data. Range fallocate paths are sensitive to page-cache invalidation and DIO ordering. Compressed files have many unsupported combinations, especially DIO, writable mmap, external compression without `CONFIG_NTFS3_LZX_XPRESS`, and deduplicated/encrypted data. Last-writer release can still fail while allocating delayed blocks or trimming preallocation, so callers must handle release-time errors.
