# File Research: sources/os/linux/linux/fs/nilfs2/dat.c

This file implements the NILFS2 DAT, the disk address translation metadata file. DAT entries map virtual block numbers to physical block numbers and track virtual-block lifetimes across checkpoints.

Data model:
- `struct nilfs_dat_info` extends metadata-file state with:
  - persistent allocator cache
  - shadow map for copy-on-write/frozen metadata support
- Each DAT entry stores:
  - `de_start`: first checkpoint where the virtual block is valid
  - `de_end`: ending checkpoint/lifetime marker
  - `de_blocknr`: current physical block number, or zero when unassigned/free

Allocation and lifetime:
- `nilfs_dat_prepare_alloc()` reserves an allocator entry and gets its DAT entry block.
- `nilfs_dat_commit_alloc()` initializes lifetime to `[1, max]` with no physical block yet.
- `nilfs_dat_prepare_start()`/`commit_start()` set the current checkpoint and physical block number when a virtual block is written.
- `nilfs_dat_prepare_end()` validates lifetime and prepares freeing if the entry has no physical block.
- `nilfs_dat_commit_end()` sets `de_end`, and frees allocator state when appropriate.
- Update is implemented as end-old plus alloc-new through prepare/commit/abort helpers.

Translation and movement:
- `nilfs_dat_translate()` returns the physical block number for a virtual block, using frozen buffers during normal operation if a DAT block has been redirected.
- `nilfs_dat_move()` changes the physical block number for GC relocation. Before modifying the live buffer, it freezes a copy so non-GC translation does not expose an uncommitted block number.
- `nilfs_dat_mark_dirty()` marks the DAT block containing a virtual block entry dirty.
- `nilfs_dat_freev()` frees multiple virtual block numbers through the persistent allocator.

Information query:
- `nilfs_dat_get_vinfo()` fills user-facing virtual block info arrays by reading relevant DAT entry blocks and copying lifetime/physical block fields.

Error handling:
- Missing DAT entry blocks for managed virtual block numbers are logged as metadata corruption and converted to `-EINVAL` in `nilfs_dat_prepare_entry()`.
- `nilfs_dat_prepare_end()` rejects entries whose start checkpoint is greater than the current checkpoint.
- `nilfs_dat_move()` rejects moves of entries with zero physical block number.

Initialization:
- `nilfs_dat_read()` validates entry size, gets `NILFS_DAT_INO`, initializes metadata and palloc block groups, installs a distinct lockdep class, sets up the palloc cache and shadow map, attaches a B-tree node cache, and reads the raw inode.
