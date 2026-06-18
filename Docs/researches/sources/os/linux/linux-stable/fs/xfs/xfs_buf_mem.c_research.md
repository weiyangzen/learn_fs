# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_buf_mem.c

## Purpose
Provides a shmem-backed XFS buffer target for in-memory files, mainly for online fsck staging structures that want to reuse buffer-cache and btree infrastructure without a block device.

## Main APIs
- `xmbuf_alloc` creates an unlinked kernel shmem file, configures an `xfs_buftarg`, and sets memory-buffer sector geometry.
- `xmbuf_free` destroys the buftarg and drops the shmem file.
- `xmbuf_map_backing_mem` maps exactly one page-sized buffer to a shmem folio.
- `xmbuf_verify_daddr` checks that an address is within the shmem maximum file size.
- `xmbuf_finalize` discards stale folios or runs the buffer structural verifier.
- `xmbuf_trans_bdetach` forcibly detaches a memory buffer from a transaction without writeback.

## Key Behavior
The only supported block size is `PAGE_SIZE`; buffers must have one map, page-aligned positions, and no highmem folios. Folios are marked dirty to prevent reclaim after the buffer drops its reference. Stale buffers call `shmem_truncate_range` to discard backing memory.

## Dependencies and Invariants
Uses tmpfs/shmem, page cache folios, XFS buftarg initialization/destruction, buffer log item flags, and verifier error reporting. Caller is responsible for concurrency; VFS freezer/inode locking is intentionally not used.
