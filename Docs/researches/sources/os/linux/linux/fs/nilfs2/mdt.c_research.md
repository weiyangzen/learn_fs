# File Research: sources/os/linux/linux/fs/nilfs2/mdt.c

This file implements generic NILFS2 metadata-file support. Metadata files are regular-looking inodes backed by bmaps, with special address-space operations, block create/read/delete helpers, dirty handling, and shadow-map support.

Metadata block creation/read:
- `nilfs_mdt_insert_new_block()` inserts a new bmap entry, zeroes and optionally initializes the block, marks it uptodate/dirty, marks the metadata inode dirty, and traces the insertion.
- `nilfs_mdt_create_block()` wraps buffer allocation and insertion in a NILFS transaction, handling races with existing blocks.
- `nilfs_mdt_submit_block()` grabs a metadata buffer, handles cache hits, locks for normal read or readahead, looks up the physical block through the inode bmap, maps the buffer, submits I/O, and returns internal `-EEXIST`/`-EBUSY` states.
- `nilfs_mdt_read_block()` reads one block and optionally readaheads up to `NILFS_MDT_MAX_RA_BLOCKS`, waits for the first block, and reports read failures.

Public block APIs:
- `nilfs_mdt_get_block()` reads or creates a metadata block, retrying if create races with another insertion.
- `nilfs_mdt_find_block()` finds the first existing metadata block in a range by trying the start block then seeking the next bmap key.
- `nilfs_mdt_delete_block()` deletes a bmap entry, marks metadata dirty, and forgets the cached block.
- `nilfs_mdt_forget_block()` clears a buffer’s dirty state and tries to invalidate the containing folio.

Dirty/writeback:
- `nilfs_mdt_fetch_dirty()` promotes bmap dirty state to inode dirty state.
- `nilfs_mdt_write_folio()` discards dirty metadata folios after read-only remount, otherwise redirties and triggers segment construction on synchronous writeback.
- `nilfs_mdt_writeback()` iterates writeback folios through that helper.
- Default metadata address-space ops use buffer dirtying, invalidation, custom writepages, and buffer migration.

Metadata inode lifecycle:
- `nilfs_mdt_init()` allocates `struct nilfs_mdt_info`, initializes semaphore, stores it in `i_private`, sets regular-file mode, GFP mask, default metadata ops, and default file/inode ops.
- `nilfs_mdt_clear()` destroys palloc cache if present and releases any shadow inode.
- `nilfs_mdt_destroy()` frees block-group layout and metadata-private memory.
- `nilfs_mdt_set_entry_size()` calculates entries per block and first entry offset based on entry/header sizes.

Shadow maps:
- `nilfs_mdt_setup_shadow_map()` creates a shadow inode and binds it to metadata state.
- `nilfs_mdt_save_to_shadow_map()` copies dirty metadata pages and associated btnode pages to shadow inodes, then saves bmap state.
- `nilfs_mdt_freeze_buffer()` copies a buffer into the shadow inode and marks the live buffer redirected, preserving pre-update contents.
- `nilfs_mdt_get_frozen_buffer()` returns the frozen copy for readers such as DAT translation.
- `nilfs_mdt_restore_from_shadow_map()` restores dirty pages, btnode pages, and bmap state under the metadata semaphore.
- `nilfs_mdt_clear_shadow_map()` releases frozen buffers and truncates shadow data/btnode caches.

Important invariants:
- Metadata block creation happens in NILFS transaction context.
- Metadata files use bmap lookup just like normal files but have their own read/create/delete helpers.
- Shadow maps protect readers from seeing uncommitted metadata relocation state and support rollback after failed segment construction.
