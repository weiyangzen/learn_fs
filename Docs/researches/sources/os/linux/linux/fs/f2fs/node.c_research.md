# File Research: sources/os/linux/linux/fs/f2fs/node.c

Implements F2FS node management: NAT cache, free-NID allocation, node page lookup/read/writeback/truncation, fsync node tracking, roll-forward helper routines, NAT flushing, and node manager lifecycle.

Major areas:
- Memory pressure policy for free NIDs, NAT cache entries, dirty dentries, inode entries, extent caches, discard cache, and compressed pages.
- NAT cache management using radix trees plus clean/dirty lists.
- Free NID discovery and allocation from NAT pages, NAT bitmaps, free-NID bitmaps, and current segment NAT journals.
- Data-to-node path traversal for direct, indirect, and double-indirect node trees.
- Node page allocation, read, writeback, readahead, dirty accounting, and truncation.
- Fsync node ordering and writeback wait support for roll-forward recovery.
- Checkpoint-time NAT entry flushing to either current segment journal or NAT blocks.
- Mount/unmount lifecycle for node manager state and slab caches.

Important NAT/free-NID functions:
- `f2fs_check_nid_range()`: validates NID bounds and marks filesystem for fsck on corruption.
- `f2fs_get_node_info()`: resolves a NID through NAT cache, current journal, or NAT block and validates block addresses.
- `set_node_addr()`: updates NAT state, dirty set membership, checkpoint/fsync flags, and node version on deletion.
- `f2fs_try_to_free_nats()`: shrinks reclaimable clean NAT cache entries.
- `f2fs_build_free_nids()`: scans NAT state to populate the free-NID cache.
- `f2fs_alloc_nid()`, `f2fs_alloc_nid_done()`, `f2fs_alloc_nid_failed()`: allocate, commit, or roll back NID reservations.
- `f2fs_try_to_free_nids()`: shrinks excess cached free NIDs.
- `f2fs_flush_nat_entries()`: checkpoint path for dirty NAT persistence.

Important node-tree functions:
- `get_node_path()`: maps file block index to inode/direct/indirect node offsets.
- `f2fs_get_dnode_of_data()`: walks or allocates the node path for a data block, returning dnode state and current data block address.
- `f2fs_get_next_page_offset()`: computes skip-ahead offsets when walking sparse node trees.
- `truncate_node()`, `truncate_dnode()`, `truncate_nodes()`, `truncate_partial_nodes()`: remove node pages and underlying data references.
- `f2fs_truncate_inode_blocks()`: truncates node tree ranges from a file offset.
- `f2fs_truncate_xattr_node()` and `f2fs_remove_inode_page()`: remove xattr and inode node pages.

Node folio I/O:
- `f2fs_new_node_folio()` / `f2fs_new_inode_folio()`: create new node pages, update NAT to `NEW_ADDR`, fill node footer, and mark dirty.
- `read_node_folio()`: resolves NAT address and submits node read bio.
- `f2fs_ra_node_page()` and `f2fs_ra_node_pages()`: node readahead helpers.
- `f2fs_sanity_check_node_footer()`: validates nid/type/footer consistency and marks corruption.
- `f2fs_get_node_folio()`, `f2fs_get_inode_folio()`, `f2fs_get_xnode_folio()`: typed node lookup wrappers.
- `__write_node_folio()`: core node writeback path, including fsync/dentry marks, NAT address update, preflush/FUA handling, dirty count decrement, and iostat type propagation.
- `f2fs_sync_node_pages()` and `f2fs_write_node_pages()`: address-space writeback implementation.
- `f2fs_node_aops`: node mapping operations.

Fsync/recovery helpers:
- `f2fs_init_fsync_node_info()`, `f2fs_add_fsync_node_entry()`, `f2fs_del_fsync_node_entry()`, `f2fs_wait_on_node_pages_writeback()`: track fsync node write order.
- `f2fs_need_dentry_mark()`, `f2fs_is_checkpointed_node()`, `f2fs_need_inode_block_update()`: decide roll-forward marks and inode block update needs.
- `f2fs_recover_inline_xattr()`, `f2fs_recover_xattr_data()`, `f2fs_recover_inode_page()`: used by `recovery.c` to rebuild inode/xattr node state.
- `f2fs_restore_node_summary()`: reconstructs node summaries by scanning node segment blocks.

Checkpoint/NAT flushing:
- Dirty NAT entries are grouped by NAT block in `nat_entry_set`.
- `__flush_nat_entry_set()` writes dirty NATs either to the hot-data journal when space allows or to the alternate NAT block copy.
- NAT bits maintain empty/full NAT block acceleration when enabled.
- Journal NAT entries are merged back into dirty NAT sets when checkpoint needs full NAT-bit consistency.

Lifecycle:
- `f2fs_build_node_manager()` allocates `f2fs_nm_info`, initializes NAT/free-NID structures, loads NAT bits, and builds initial free NIDs.
- `f2fs_destroy_node_manager()` frees free-NID caches, NAT caches, NAT sets, bitmaps, NAT bits, and node manager state.
- `f2fs_create_node_manager_caches()` / `f2fs_destroy_node_manager_caches()` manage slab caches for NAT entries, free NIDs, NAT sets, and fsync node entries.

Error handling:
- Many paths mark `SBI_NEED_FSCK` and call `f2fs_handle_error()` for inconsistent NAT entries, invalid node references, bad block addresses, or footer mismatches.
- Writeback avoids unsafe progress during checkpoint errors and power-on recovery.
- Allocation paths include fault-injection hooks and retry loops for memory pressure.
