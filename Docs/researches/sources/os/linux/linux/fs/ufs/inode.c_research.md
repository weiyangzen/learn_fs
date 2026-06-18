# File Research: sources/os/linux/linux/fs/ufs/inode.c

Purpose: UFS inode read/write, block mapping, page-cache operations, eviction, and truncation.

Key behavior:
- `ufs_block_to_path()` maps a logical block to direct, single, double, or triple indirect offsets.
- `ufs_frag_map()` walks UFS1 32-bit or UFS2 64-bit direct/indirect pointers under sequence protection and returns a physical fragment.
- `ufs_extend_tail()`, `ufs_inode_getfrag()`, and `ufs_inode_getblock()` allocate direct fragments and indirect blocks/fragments for writes.
- `ufs_getfrag_block()` is the central `get_block_t` implementation for reads, writes, bmap, writepages, and directory chunk preparation.
- Address-space operations use generic buffer/page-cache helpers wired to `ufs_getfrag_block()`.
- `ufs_set_inode_ops()` chooses regular, directory, symlink, or special inode operation tables; fast symlinks use inline inode data.
- `ufs1_read_inode()` and `ufs2_read_inode()` convert on-disk inode formats into VFS/UFS in-core inode state.
- `ufs_iget()` validates inode number, reads the on-disk inode block, selects UFS1/UFS2 parser, initializes `i_lastfrag`, and unlocks the inode.
- `ufs1_update_inode()`, `ufs2_update_inode()`, `ufs_update_inode()`, `ufs_write_inode()`, and `ufs_sync_inode()` serialize inode state back to disk.
- `ufs_evict_inode()` truncates and frees deleted inodes.
- Truncation helpers free direct tails, full indirect branches, partial branch tails, and ensure the last partial block is allocated/zeroed before shortening.
- `ufs_setattr()` handles size changes through `ufs_truncate()` and then copies generic attributes.

Integration:
- Block allocator dependency: `ufs_new_fragments()`, `ufs_free_blocks()`, and `ufs_free_fragments()` from `balloc.c`.
- Directory dependency: exports `ufs_prepare_chunk()` and address-space operations consumed by `dir.c`.
- Inode allocation/free dependency: calls `ufs_free_inode()` on eviction.
- File and directory operation tables are installed here.

Risks and invariants:
- `truncate_mutex` serializes allocation/truncation-sensitive block mapping.
- `meta_lock` sequence locking protects data pointer reads against concurrent metadata pointer changes.
- UFS1 and UFS2 differ in pointer width and timestamp/inode layout.
- Truncation must handle fragments, full blocks, indirect blocks, and page-cache state consistently to avoid leaks or stale data.
