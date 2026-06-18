# File Research: sources/os/linux/linux/fs/ext2/inode.c

Read status: complete, 1691 lines.

This file implements ext2 inode lifecycle, indirect-block file mapping, block allocation through mapping requests, truncation/free recursion, address-space operations, iomap integration, fiemap, inode read/write, and setattr/getattr.

Key responsibilities:
- Evicts inodes with `ext2_evict_inode()`, including deleted-inode truncation, xattr deletion, reservation cleanup, and inode freeing.
- Maps logical file blocks through the ext2 direct/single/double/triple indirect tree.
- Allocates indirect branches and data blocks using `ext2_new_blocks()`.
- Splices newly allocated branches into inode metadata after race checks.
- Supports buffer-head mapping through `ext2_get_block()`.
- Supports iomap through `ext2_iomap_ops`.
- Implements folio address-space operations for buffered read/write/writeback.
- Implements DAX address-space operations.
- Truncates files and recursively frees indirect subtrees.
- Reads raw inodes from inode tables and populates VFS inodes with `ext2_iget()`.
- Writes VFS inode state back to disk with `__ext2_write_inode()`.
- Implements `getattr`, `setattr`, and `fiemap`.

Block mapping design:
- `ext2_block_to_path()` converts a logical block to offsets through direct, indirect, double-indirect, or triple-indirect levels.
- `ext2_get_branch()` reads existing indirect blocks into a chain of pointer/key/buffer triples and detects holes, I/O failures, or concurrent modification.
- `ext2_find_goal()` prefers sequential allocation based on last allocation hints, otherwise locality near previous pointers, indirect blocks, or inode block group.
- `ext2_alloc_branch()` allocates needed metadata and data blocks before linking them into the tree.
- `ext2_splice_branch()` atomically attaches the new branch and updates allocation hints and inode metadata.
- `ext2_get_blocks()` is the central lookup/create routine used by buffer-head and iomap paths.

Truncation design:
- `ext2_truncate_blocks()` skips unsupported inode types and fast symlinks.
- Truncation takes the mapping invalidate lock and `truncate_mutex`.
- `ext2_find_shared()` detaches partially truncated branches safely.
- `ext2_free_data()` coalesces contiguous data block frees.
- `ext2_free_branches()` recursively frees indirect subtrees.
- Reservation windows are discarded after truncation.

Inode read/write:
- `ext2_get_inode()` computes inode table location from inode number and group descriptor.
- `ext2_iget()` validates deleted/stale inodes, reads UID/GID, timestamps, blocks, flags, ACL fields, generation, data pointers, and installs correct inode/file ops by type.
- Fast symlinks store the symlink target in `i_data`; slow symlinks use page-cache-backed data.
- Special files decode old or new device numbers from inode block fields.
- `__ext2_write_inode()` serializes VFS inode state back to the ext2 raw inode, handles UID/GID high bits, large-file feature enabling, device encoding, and new-inode zeroing.

I/O integration:
- `ext2_iomap_begin()` maps ext2 indirect blocks into iomap records for DAX/direct/fiemap.
- Direct writes to holes inside `i_size` return `-ENOTBLK` for buffered fallback to avoid stale exposure on non-extent storage.
- Buffered address-space operations use mpage and block helpers with `ext2_get_block()`.
- DAX writeback uses `dax_writeback_mapping_range()`.

Concurrency and safety:
- `truncate_mutex` serializes block tree mutation and truncation.
- `i_meta_lock` protects verification of indirect-chain consistency.
- Mapping invalidate lock protects truncation against DAX/page-cache interactions.
- Branch allocation prepares all blocks before publishing pointers, reducing recovery complexity on allocation failure.
- DAX newly allocated blocks are zeroed before being linked into the tree.

Research notes:
- This is the core ext2 data mapping file.
- It demonstrates classic Unix indirect-block mapping adapted to modern Linux iomap, DAX, folio, quota, and writeback infrastructure.
