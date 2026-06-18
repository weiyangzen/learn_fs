# File Research: sources/os/linux/linux/fs/nilfs2/mdt.h

`mdt.h` defines the shared in-memory framework for NILFS metadata files such as DAT, cpfile, sufile, and ifile. `struct nilfs_mdt_info` is stored in `inode->i_private` and carries the metadata operation semaphore, per-blockgroup locks, entry sizing, persistent allocator cache, optional shadow mapping, and group geometry.

The header also defines `struct nilfs_shadow_map`, used when metadata updates need a recoverable shadow copy of bmap state and page cache contents. This is central to cleaner/GC flows that must stage metadata changes and roll them back on failure.

Important interfaces include metadata block lookup/allocation/deletion (`nilfs_mdt_get_block`, `nilfs_mdt_find_block`, `nilfs_mdt_delete_block`, `nilfs_mdt_forget_block`), dirty detection (`nilfs_mdt_fetch_dirty`), lifecycle (`nilfs_mdt_init`, `nilfs_mdt_clear`, `nilfs_mdt_destroy`), entry layout setup, and shadow-map save/restore/clear/freeze helpers.

The inline helpers mark or clear `NILFS_I_DIRTY` on the owning NILFS inode, expose the current checkpoint number via `nilfs_mdt_cno()`, and return blockgroup locks for palloc-style metadata. The design assumes only metadata inodes have non-NULL `i_private`; `nilfs_is_metadata_file_inode()` is used by inode destruction in `super.c`.
