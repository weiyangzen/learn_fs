# File Research: sources/os/linux/linux-stable/fs/f2fs/node.c

## Purpose

`node.c` implements F2FS node and NAT management. It is responsible for node address translation, NAT cache state, free nid discovery/allocation, node-page lookup/allocation/truncation, node writeback/fsync ordering, roll-forward recovery helpers, NAT checkpoint flushing, node manager initialization, and cache teardown.

## Core Concepts

- NAT maps nid to node owner inode, physical block address, and version.
- Free nids are derived from NAT entries whose block address is `NULL_ADDR`.
- Node pages form the file block-index tree: inode node, direct nodes, indirect nodes, and double-indirect nodes.
- Dirty NAT entries are grouped by NAT block offset into `nat_entry_set` objects for checkpoint flushing.
- Dirty node pages are written copy-on-write style, then NAT entries are updated to the newly allocated node block.
- Fsync node pages are tracked in sequence order to support atomic/fsync recovery semantics.

## Memory Pressure

- `f2fs_available_free_memory()`
  - Provides type-specific memory admission decisions for free nids, NAT entries, dirty dentries, ino entries, extent caches, discard cache, and compressed pages.
  - Uses system low memory, F2FS thresholds, dirty-writeback pressure, and cache counts.
  - Prevents excessive NAT caching via `excess_cached_nats()`.

## NAT Cache Management

- `f2fs_check_nid_range()`
  - Rejects nids below root ino or beyond `max_nid`.
  - Marks filesystem for fsck and reports corruption.

- `get_current_nat_folio()` / `get_next_nat_folio()`
  - Read the current NAT block or copy it to the alternate NAT block.
  - `get_next_nat_folio()` flips the NAT bitmap to the next copy.

- `__alloc_nat_entry()` / `__free_nat_entry()`
  - Allocate/free cached NAT entries.
  - New entries receive nid and reset checkpoint/fsync flags.

- `__init_nat_entry()`
  - Inserts NAT entry into the radix tree.
  - Initializes from raw NAT when available.
  - Places clean entries on reclaimable LRU or initializes dirty entries for checkpoint state.

- `__lookup_nat_cache()`
  - Looks up cached NAT entry.
  - Moves clean, non-dirty lookup hits to the tail of the reclaimable list when not being dirtied.

- `__set_nat_cache_dirty()`
  - Marks a NAT entry dirty.
  - Groups non-preallocation updates under a `nat_entry_set`.
  - Tracks dirty NAT count and reclaimable count.
  - Treats `NEW_ADDR` entries as preallocated and not yet assigned to a NAT block set.

- `__clear_nat_cache_dirty()`
  - Moves flushed entries back to clean reclaimable NAT list.
  - Updates dirty/reclaimable counters and set entry counts.

- `set_node_addr()`
  - Central NAT state transition routine.
  - Allocates or reuses a NAT cache entry.
  - Handles reallocation to `NEW_ADDR`, deletion to `NULL_ADDR`, and valid block address updates.
  - Increments NAT version when a node is removed.
  - Marks entries dirty and updates fsync-related NAT flags.
  - Maintains inode NAT flags for last fsync and fsynced inode tracking.

- `f2fs_get_node_info()`
  - Resolves node info from NAT cache, current NAT journal, or NAT block.
  - Avoids lock-order issues around checkpoint and journal locks by retrying when needed.
  - Validates resolved block address and quota-file NAT consistency.
  - Caches NAT entries outside checkpoint-sensitive paths.

- `f2fs_try_to_free_nats()`
  - Shrinks reclaimable clean NAT cache entries from the LRU list.

## Fsync Node Tracking

- `f2fs_init_fsync_node_info()`
  - Initializes fsync node list, lock, sequence id, and count.

- `f2fs_add_fsync_node_entry()`
  - Records a folio in fsync write order and returns its sequence id.

- `f2fs_del_fsync_node_entry()`
  - Removes a completed fsync node entry and drops the folio reference.

- `f2fs_reset_fsync_node_info()`
  - Resets fsync segment sequence id.

- `f2fs_need_dentry_mark()`
  - Determines whether an inode node needs a dentry mark for roll-forward recovery.

- `f2fs_is_checkpointed_node()`
  - Reports whether a nid is known checkpointed.

- `f2fs_need_inode_block_update()`
  - Checks NAT fsync flags to decide whether inode block update is required.

## Node Tree Pathing and Lookup

- `get_node_path()`
  - Converts a logical data block index into offsets through the F2FS node tree.
  - Handles direct inode addresses, two direct nodes, two indirect-node regions, and one double-indirect region.
  - Returns path level or `-E2BIG`.

- `f2fs_get_next_page_offset()`
  - Computes next page offset after an absent node lookup, allowing callers to skip unmapped ranges.

- `f2fs_get_dnode_of_data()`
  - Walks inode/direct/indirect/double-indirect node path to locate the dnode for a logical page index.
  - Can allocate missing nodes in `ALLOC_NODE` mode.
  - Can perform sibling readahead in `LOOKUP_NODE_RA` mode.
  - Detects self-referential node mapping corruption.
  - Handles inline-data special case.
  - Updates compressed read extent cache on readonly compressed files when clusters are contiguous.
  - Returns enough level/offset context on `-ENOENT` for callers to skip forward.

## Node Truncation and Removal

- `truncate_node()`
  - Invalidates the node block, decrements valid node/inode counts, updates NAT to `NULL_ADDR`, clears dirty page state, and invalidates node mapping page.
  - Removes orphan inode and marks inode synced for inode nodes.

- `truncate_dnode()`
  - Loads a direct node, validates ownership, truncates all data blocks in it, and removes the node.

- `truncate_nodes()`
  - Recursively truncates indirect and double-indirect subtrees.
  - Clears nid pointers in parent nodes and tracks whether parent changed.

- `truncate_partial_nodes()`
  - Handles partial truncation along an indirect path before whole-subtree truncation.

- `f2fs_truncate_inode_blocks()`
  - Removes all node/data block references from a given logical offset onward.
  - Handles direct, indirect, and double-indirect regions.
  - Marks fsck-needed on invalid node references but may continue when possible.

- `f2fs_truncate_xattr_node()`
  - Removes the external xattr node and clears inode xattr nid.

- `f2fs_remove_inode_page()`
  - Removes an inode node after truncating xattr node and possible inline-data block.
  - Validates unexpected `i_blocks` values and respects checkpoint error state.

## Node Allocation and Reading

- `f2fs_new_inode_folio()`
  - Allocates the inode node page for a new inode.

- `f2fs_new_node_folio()`
  - Allocates a node cache folio and increments valid node count.
  - Initializes NAT state to `NEW_ADDR`.
  - Fills node footer and cold-node mark.
  - Marks page dirty and records xattr nid when allocating xattr node.
  - Increments valid inode count for inode node offset `0`.

- `read_node_folio()`
  - Reads a node page from the block address resolved through NAT.
  - Rejects `NULL_ADDR`/`NEW_ADDR`.
  - Verifies checksum for already uptodate pages.
  - Accounts node read I/O through iostat.

- `f2fs_ra_node_page()`
  - Readaheads a node page if it is not already cached.

- `f2fs_sanity_check_node_footer()`
  - Validates footer nid and expected node type.
  - Distinguishes regular, inode, xattr, and non-inode node expectations.
  - Marks fsck-needed and reports `ERROR_INCONSISTENT_FOOTER` on mismatch.

- `__get_node_folio()`
  - Shared locked node-folio acquisition path.
  - Reads from disk if needed, handles retry if folio identity changes, verifies uptodate state, checksum, and footer consistency.
  - Optional parent-based readahead.

- Public wrappers:
  - `f2fs_get_node_folio()`
  - `f2fs_get_inode_folio()`
  - `f2fs_get_xnode_folio()`

## Node Writeback

- `flush_inline_data()`
  - Flushes dirty inline data for an inode before inode eviction/writeback conflicts.

- `last_fsync_dnode()`
  - Finds the last dirty warm dnode for an inode, used to mark the final fsync node during atomic fsync.

- `__write_node_folio()`
  - Core node writeback routine.
  - Handles checkpoint error, POR in-progress, and asynchronous warm dnode deferral.
  - Validates node footer and NAT block address.
  - Applies preflush/FUA for atomic writes unless barriers are disabled.
  - Sets fsync and dentry marks.
  - Adds warm fsync nodes to global sequence list before clearing dirty state.
  - Calls `f2fs_do_write_node_page()`, updates NAT via `set_node_addr()`, decrements dirty node page count, and optionally balances filesystem state.

- `f2fs_write_single_node_folio()`
  - Writes one node folio for GC or synchronous callers.

- `f2fs_move_node_folio()`
  - Moves a node folio during GC using foreground/background sync mode.

- `f2fs_fsync_node_pages()`
  - Writes dirty warm dnodes for a specific inode.
  - Marks the final atomic fsync dnode.
  - Updates inode page if dirty inode metadata must be folded into the inode node.
  - Submits merged node writes for the inode.

- `f2fs_flush_inline_data()`
  - Scans dirty inode node pages and flushes inline data marked on node folios.

- `f2fs_sync_node_pages()`
  - General node writeback scanner.
  - Flush order:
    1. indirect nodes
    2. dentry dnodes
    3. file dnodes
  - Gives priority to synchronous writers.
  - Flushes inline data and dirty inode metadata before node writeback in balancing contexts.
  - Submits merged node writes at the end.

- `f2fs_wait_on_node_pages_writeback()`
  - Waits for fsync node writeback up to a sequence id.
  - Checks node mapping writeback errors.

- `f2fs_write_node_pages()`
  - Address-space writepages hook for node mapping.
  - Skips during POR.
  - Performs background balancing.
  - Avoids small async writeback batches and avoids deadlock with synchronous node writeback.
  - Calls `f2fs_sync_node_pages()` under a block plug.

- `f2fs_dirty_node_folio()`
  - Address-space dirty_folio hook.
  - Marks uptodate, updates checksum under checkfs, increments dirty node count, and sets F2FS reference bit.

- `f2fs_node_aops`
  - Node mapping address-space operations table.

## Free Nid Management

- `__lookup_free_nid_list()`
  - Looks up free/preallocated nid state in radix tree.

- `__insert_free_nid()`, `__remove_free_nid()`, `__move_free_nid()`
  - Maintain radix tree, free list, and `FREE_NID`/`PREALLOC_NID` counters.

- `update_free_nid_bitmap()`
  - Updates per-NAT-block free nid bitmap and free count, but only after that NAT block has been scanned/known.

- `add_free_nid()`
  - Adds a nid as free after validating range and checking NAT cache conflicts.
  - During free-nid building, avoids stale nids that are preallocated or dirtied concurrently.
  - Updates free nid bitmap and `available_nids` when requested.

- `remove_free_nid()`
  - Removes a nid from the free list when it is no longer free.

- `scan_nat_page()`
  - Scans a NAT block and adds free nids for `NULL_ADDR` entries.
  - Treats `NEW_ADDR` in NAT as corruption.

- `scan_curseg_cache()`
  - Reconciles free nid state against NAT entries in the current hot data journal.

- `scan_free_nid_bits()`
  - Builds free nid list from cached free-nid bitmaps and then reconciles current segment journal.

- `__f2fs_build_free_nids()` / `f2fs_build_free_nids()`
  - Populate free nid list from nat_bits/free-nid bitmap or by scanning NAT pages.
  - Uses `build_lock` to serialize builders.
  - Readaheads NAT pages and advances `next_scan_nid`.

- `f2fs_alloc_nid()`
  - Allocates a nid from free list by moving it to `PREALLOC_NID`.
  - Decrements available nid count and clears free nid bitmap.
  - Builds free nids synchronously if needed.
  - Refuses allocation when no available nids remain or fault injection triggers.

- `f2fs_alloc_nid_done()`
  - Completes a successful preallocated nid by removing and freeing its state entry.

- `f2fs_alloc_nid_failed()`
  - Returns a preallocated nid to free state or drops it under memory pressure.
  - Restores available nid count and bitmap state.

- `f2fs_try_to_free_nids()`
  - Shrinks excess free nid cache entries above `MAX_FREE_NIDS`.

## Recovery Helpers

- `f2fs_recover_inline_xattr()`
  - Replays inline xattr state from recovered node folio into the inode folio.
  - Adjusts inline xattr flags and statistics.

- `f2fs_recover_xattr_data()`
  - Invalidates previous xattr node, allocates a new xattr nid/node, updates inode page, and copies recovered xattr node content.

- `f2fs_recover_inode_page()`
  - Recreates a missing inode page during roll-forward recovery.
  - Removes the ino from free nid cache.
  - Copies safe inode metadata from recovered folio, resets size/blocks/links/xattr nid, preserves selected extra attributes, sets NAT to `NEW_ADDR`, increments valid node/inode counts, and marks inode folio dirty.

- `f2fs_restore_node_summary()`
  - Rebuilds node summary entries by scanning node segment blocks and reading footer nids.

## NAT Checkpoint Flushing

- `remove_nats_in_journal()`
  - Moves NAT journal entries into dirty NAT cache so checkpoint can write a coherent NAT state.
  - Adjusts available nid count for free NAT entries that will be re-added.

- `__adjust_nat_entry_set()`
  - Orders dirty NAT sets by entry count for journal/NAT block flushing efficiency.

- `__update_nat_bits()`
  - Maintains empty/full NAT block bitmaps when NAT bits are enabled.

- `__flush_nat_entry_set()`
  - Flushes a dirty NAT set either to the hot data summary journal or to the alternate NAT block.
  - Converts cached `node_info` into raw NAT entries.
  - Resets NAT flags, clears dirty state, and updates free nid tracking.
  - Updates nat_bits when writing NAT blocks directly.
  - Frees empty `nat_entry_set`.

- `f2fs_flush_nat_entries()`
  - Main checkpoint NAT flush routine.
  - Optionally removes NAT journal entries first when nat_bits are enabled or journal space is insufficient.
  - Sorts NAT sets, readaheads NAT pages for direct flushes, and flushes each set.

## Node Manager Initialization and Teardown

- `__get_nat_bitmaps()`
  - Loads nat_bits from checkpoint area when enabled.
  - Verifies checkpoint version/CRC before accepting nat_bits.
  - Disables nat_bits if validation fails.

- `load_free_nid_bitmap()`
  - Initializes free nid bitmap from empty NAT bits and marks full NAT blocks as scanned.

- `init_node_manager()`
  - Initializes NAT geometry, max nid, available nid count, thresholds, radix trees, lists, locks, NAT bitmap, nat_bits, and checkfs mirror bitmap.

- `init_free_nid_cache()`
  - Allocates per-NAT-block free nid bitmaps, NAT block scanned bitmap, and per-block free nid counts.

- `f2fs_build_node_manager()`
  - Allocates `sbi->nm_info`, initializes manager and free nid cache, loads nat_bits-derived state, then builds initial free nids.

- `f2fs_destroy_node_manager()`
  - Frees free nid list, NAT cache, NAT set cache, bitmaps, nat_bits, mirror bitmap, and manager structure.
  - Uses assertions to catch leaked free/preallocated nids and NAT entries.

- `f2fs_create_node_manager_caches()` / `f2fs_destroy_node_manager_caches()`
  - Manage slab caches for NAT entries, free nid entries, NAT entry sets, and fsync node entries.

## Concurrency and Consistency

- `nat_tree_lock` protects NAT radix trees and NAT entry sets.
- `nat_list_lock` protects NAT clean/dirty list movements.
- `nid_list_lock` protects free/preallocated nid radix tree, list, counters, and bitmaps.
- `build_lock` serializes free nid construction.
- `node_write` coordinates node writes with NAT state changes.
- `fsync_node_lock` protects fsync node sequence list.
- Checkpoint and journal lock ordering is carefully handled in `f2fs_get_node_info()` and NAT flush paths.
- Corruption detection sets `SBI_NEED_FSCK` and reports specific F2FS error categories for invalid nid ranges, NAT inconsistencies, footer mismatches, summaries, and node references.
