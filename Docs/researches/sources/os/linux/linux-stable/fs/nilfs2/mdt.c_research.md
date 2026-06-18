# File Research: sources/os/linux/linux-stable/fs/nilfs2/mdt.c

## Summary
Implements common NILFS metadata-file support. Metadata files are represented as regular inodes with NILFS bmaps, specialized address-space operations, palloc state, and optional shadow maps.

## Main Responsibilities
- Creates, reads, finds, deletes, and forgets metadata blocks.
- Inserts newly allocated metadata blocks into the file bmap within NILFS transactions.
- Provides metadata address-space writeback behavior.
- Initializes, clears, and destroys metadata inode private state.
- Configures metadata entry sizing.
- Creates and manages shadow maps used to preserve old metadata state during copy-on-write updates.
- Freezes and retrieves redirected buffers.
- Restores or clears shadow map state after segment construction outcomes.

## Important Behavior
`nilfs_mdt_get_block()` first tries to read an existing block and, when `create` is true and the block is a hole, creates it transactionally. New block insertion calls `nilfs_bmap_insert()`, initializes the block contents, marks the buffer uptodate and dirty, and marks the metadata inode dirty.

`nilfs_mdt_read_block()` reads one metadata block through the inode bmap and may submit up to 15 readahead blocks. `nilfs_mdt_find_block()` uses bmap seek when the starting block is a hole, allowing sparse metadata scans such as checkpoint listing.

Metadata writeback redirties folios and, for synchronous writeback, triggers segment construction instead of normal block writeout. If the filesystem is read-only, dirty metadata folios are discarded.

`nilfs_mdt_setup_shadow_map()` creates a shadow inode plus associated node-cache inode. `nilfs_mdt_save_to_shadow_map()` copies dirty data pages, dirty B-tree-node-cache pages, and bmap state into the shadow. `nilfs_mdt_restore_from_shadow_map()` clears current dirty pages, copies pages back, restores bmap state, and clears palloc caches. `nilfs_mdt_clear_shadow_map()` releases frozen buffers and truncates shadow caches.

`nilfs_mdt_freeze_buffer()` copies a buffer into the shadow inode cache, links it on `frozen_buffers`, and marks the original buffer redirected. DAT translation can then read the frozen copy until uncommitted changes are safe.

## Risks
Metadata files do not use normal writeback; segment construction is the persistence path. Shadow-map handling must include both metadata data pages and associated B-tree node pages. Forget/delete paths clear buffer dirty state and may fail to invalidate busy folios.
