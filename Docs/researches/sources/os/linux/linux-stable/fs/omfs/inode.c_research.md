# File Research: sources/os/linux/linux-stable/fs/omfs/inode.c

## Scope

This file implements OMFS module registration, filesystem context parsing, superblock mounting, inode allocation/loading/writing/eviction, checksum generation, statfs, mount option display, and free-bitmap loading.

## Main APIs

- `omfs_bread()` reads an OMFS cluster/block after range checking.
- `omfs_new_inode()` allocates blocks, initializes VFS inode state, installs OMFS ops, hashes the inode, and marks it dirty.
- `omfs_iget()` loads an inode from disk, validates self pointer, applies mount uid/gid/masks, timestamps, mode, ops, size, and unlocks it.
- `omfs_sync_inode()` and `omfs_write_inode()` serialize in-memory inode state into on-disk OMFS inode blocks.
- Super operations: write inode, evict inode, put super, statfs, show options.
- Filesystem context ops parse `uid`, `gid`, `umask`, `dmask`, and `fmask`, then mount with `get_tree_bdev()`.

## Control Flow

- Mount reads block 0 as OMFS superblock, checks magic, loads counts, block sizes, mirrors, root inode, and system block size.
- It validates maximum block count, sys block size, data block size, root-block consistency, bitmap location, and cluster size.
- The kernel block size is first set to 512, then reset to OMFS system block size; `s_block_shift` converts OMFS cluster numbers to Linux block numbers.
- Root block provides bitmap location, cluster size, and root directory inode.
- `omfs_get_imap()` loads the free-space bitmap into an array of block-sized memory copies. If no bitmap exists (`~0ULL`), it skips allocation.
- `__omfs_write_inode()` writes header fields, type, size, millisecond ctime, CRC, XOR checksum, and mirrors the inode block to `s_mirrors - 1` following blocks.
- `omfs_evict_inode()` truncates page cache, clears inode, frees regular-file extents for unlinked files, then frees inode mirror blocks.

## Risks And Invariants

- `omfs_put_super()` frees only the `s_imap` pointer array, not each per-block `kmemdup()` bitmap buffer, which looks like a memory leak on unmount.
- `omfs_fill_super()` frees `sbi` directly on mount failure without clearing `sb->s_fs_info` and without freeing loaded bitmap sub-buffers.
- `omfs_evict_inode()` clears two inode blocks unconditionally, while allocation used `sbi->s_mirrors`; this may mismatch mirror counts other than two.
- `omfs_iget()` has no default failure for unknown `i_type`; it can unlock and return an inode with incomplete mode/ops if disk type is invalid.
- On-disk checksum update is write-only here; read paths validate self pointer but do not verify CRC/XOR.
