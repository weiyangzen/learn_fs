# File Research: sources/os/linux/linux/fs/nilfs2/inode.c

This file implements NILFS2 inode lifecycle, block mapping callbacks, address-space operations, inode read/write conversion, truncation, eviction, dirty tracking, permission checks, and fiemap.

Block mapping and I/O:
- `nilfs_get_block()` is the core VFS block mapper. It looks up contiguous mappings through the inode bmap under the DAT metadata semaphore.
- On missing blocks with `create`, it starts a transaction, inserts a bmap entry using the supplied buffer head, marks the inode dirty/sync, commits, and returns a delayed new mapped buffer.
- Read folio and readahead use `mpage_*` with `nilfs_get_block()`.
- Writepages construct a dsync segment for synchronous writeback; read-only mode discards dirty pages.
- `nilfs_dirty_folio()` marks mapped buffers dirty and updates NILFS dirty-block accounting.
- `nilfs_write_begin()` and `nilfs_write_end()` wrap generic block writes in NILFS transactions.

Direct I/O:
- Writes return `0`, effectively falling back to buffered I/O.
- Reads use `blockdev_direct_IO()` and `nilfs_get_block()`.

Inode allocation and reading:
- `nilfs_new_inode()` allocates a VFS inode, allocates an ifile entry, initializes owner/timestamps/flags/generation, reads an empty bmap for regular/dir/symlink files, inserts into inode cache, and initializes ACL.
- `nilfs_read_inode_common()` imports mode, uid/gid, links, size, timestamps, blocks, flags, generation, and bmap data from raw inode storage.
- `__nilfs_read_inode()` reads the raw inode from ifile, then installs operation tables based on file type.
- `nilfs_iget()`, `nilfs_iget_locked()`, and `nilfs_ilookup()` use custom iget comparison keyed by inode number, root, checkpoint number, and inode type.

Associated inodes:
- `nilfs_attach_btree_node_cache()` creates or gets a BTNC inode associated one-to-one with a data/metadata inode, sharing the bmap pointer and using btnode cache initialization.
- `nilfs_detach_btree_node_cache()` disconnects and drops the associated inode.
- `nilfs_iget_for_gc()` creates GC dummy inodes.
- `nilfs_iget_for_shadow()` creates shadow-map inodes and attaches a btnode cache.

Raw inode export:
- `nilfs_write_inode_common()` writes generic inode fields to a raw NILFS inode.
- `nilfs_update_inode()` maps the raw ifile entry, clears it for new inodes, sets sync state if needed, writes common fields, and writes device code for special files.

Truncation and eviction:
- `nilfs_truncate_bmap()` repeatedly truncates bmap entries in chunks up to `NILFS_MAX_TRUNCATE_BLOCKS`, retrying some memory-pressure cases.
- `nilfs_truncate()` handles page truncation, bmap truncation, timestamp updates, dirty marking, and transaction commit.
- `nilfs_evict_inode()` handles live/unlinked/bad inode paths. For unlinked writable inodes it truncates bmap, marks inode dirty, deletes the ifile entry, decrements root inode count, and commits.

Dirty tracking:
- `nilfs_load_inode_block()` caches and refreshes the ifile buffer for an inode under `ns_inode_lock`.
- `nilfs_set_file_dirty()` increments dirty block count, sets inode dirty state, grabs inode reference if needed, and queues it on `ns_dirty_files`.
- `__nilfs_mark_inode_dirty()` updates raw inode storage and marks the ifile dirty unless NILFS is purging.
- `nilfs_dirty_inode()` either marks metadata inodes dirty directly or wraps normal inode dirtying in a transaction.

Permissions and attributes:
- `nilfs_setattr()` wraps truncate and generic setattr in a NILFS transaction and handles ACL chmod.
- `nilfs_permission()` rejects writes to non-current checkpoint roots with `-EROFS`.
- `nilfs_set_inode_flags()` maps NILFS persistent flags to VFS inode flags.

Fiemap:
- `nilfs_fiemap()` walks requested logical blocks, combines bmap lookup results with delayed allocation extents, emits merged extents, and marks delayed allocations with `FIEMAP_EXTENT_DELALLOC`.

Important invariants:
- Normal writable operations happen in NILFS transaction context.
- Snapshot roots are read-only except the current checkpoint root.
- Associated btnode, GC, and shadow inodes are differentiated by custom inode type bits in iget matching.
- DAT semaphore protects bmap lookup paths that translate virtual blocks.
