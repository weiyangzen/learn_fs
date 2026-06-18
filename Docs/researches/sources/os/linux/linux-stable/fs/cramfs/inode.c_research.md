# File Research: sources/os/linux/linux-stable/fs/cramfs/inode.c

This file implements the CramFs readonly filesystem VFS integration, mount paths, inode construction, block reading, directory lookup, folio reads, decompression, and direct MTD mapping support.

Key responsibilities:
- Defines in-memory superblock state `struct cramfs_sb_info`.
- Creates VFS inodes from on-disk `struct cramfs_inode`.
- Reads CramFs image data from either block devices or linearly mapped MTD memory.
- Supports optional direct physical-memory mmap for suitable uncompressed MTD-backed files.
- Parses and validates the CramFs superblock.
- Implements directory iteration, lookup, page-cache folio filling, statfs, mount, remount, and kill-super behavior.

Important control flow:
- Inode creation:
  - `cramino()` derives stable inode numbers from data offsets when possible.
  - `get_cramfs_inode()` assigns file operations by file type, sets uid/gid/mode, size, blocks, and zero timestamps.
- Image reads:
  - `cramfs_blkdev_read()` maintains a two-entry static read buffer cache over groups of pages.
  - `cramfs_direct_read()` returns pointers into linearly mapped memory, or zero page for out-of-range.
  - `cramfs_read()` selects direct MTD or block-device path.
- Direct mapping:
  - `cramfs_get_block_range()` verifies a run of direct, uncompressed, contiguous blocks.
  - `cramfs_physmem_mmap()` attempts full or partial PFN insertion for mapped MTD images, falling back to normal paging when unsuitable.
- Mount:
  - `cramfs_read_super()` reads magic at offset 0 or 512, validates endianness, flags, root mode, root offset, and fsid data.
  - `cramfs_blkdev_fill_super()` allocates super info and invalidates static read buffers.
  - `cramfs_mtd_fill_super()` maps one page, reads size, then remaps the whole image.
  - `cramfs_finalize_super()` creates the root inode/dentry and marks readonly.
- File reads:
  - `cramfs_read_folio()` resolves block pointer format, supports direct/uncompressed blocks, compressed blocks with optional two-byte length, holes, previous direct pointer edge cases, decompression, and zero-fill tail.
- Directory operations:
  - `cramfs_readdir()` emits padded directory entries.
  - `cramfs_lookup()` scans entries, optionally using sorted-directory early exit.

Dependencies:
- Uses zlib wrapper `cramfs_uncompress_block()` from `uncompress.c`.
- Uses CramFs on-disk definitions from `<uapi/linux/cramfs_fs.h>`.
- Uses MTD helpers when configured and block-device helpers when configured.

Risks and invariants:
- Global `read_mutex` protects static read buffers and serialized decompression/read parsing.
- The block-device cache is static and shared, so buffer invalidation on mount matters.
- Filesystem is always mounted readonly.
- CramFs has intentionally limited metadata fidelity: no real timestamps and weak directory nlink precision.
- Direct mmap is possible only for direct, uncompressed, contiguous, page-aligned physical data and avoids mapping a shared dirty tail page.
