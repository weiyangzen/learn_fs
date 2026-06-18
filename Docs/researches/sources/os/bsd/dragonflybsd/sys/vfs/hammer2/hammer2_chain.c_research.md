# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_chain.c

## Purpose
Implements HAMMER2's core in-memory chain abstraction: keyed topology nodes for volume roots, inodes, indirect blocks, freemap blocks, data blocks, and dirents, including lifecycle, locking, lookup, copy-on-write modification, insertion/deletion, indirect-node maintenance, blockref array management, checksum handling, and debugging.

## Key Elements
- `hammer2_chain_cmp()` defines the RB-tree ordering by blockref key ranges and treats overlap as equality, making overlapping chains invalid.
- `hammer2_chain_setflush()` propagates `HAMMER2_CHAIN_ONFLUSH` upward until an inode or volume root so the flusher can find modified/update subtrees.
- `hammer2_chain_alloc()` and `hammer2_chain_init()` allocate and initialize disconnected chains, set PFS boundary state, derive physical byte size from `data_off` radix, and initialize locks/RB trees.
- `hammer2_chain_ref()`, `hammer2_chain_ref_hold()`, `hammer2_chain_drop()`, `hammer2_chain_lastdrop()`, `hammer2_chain_unhold()`, `hammer2_chain_drop_unhold()`, and `hammer2_chain_rehold()` implement reference/hold lifecycle, delayed disposal, parent unlinking, data-drop behavior, and nonrecursive parent re-drop handling.
- `hammer2_chain_lock()`, `hammer2_chain_load_data()`, and `hammer2_chain_unlock()` provide shared/exclusive chain locking with optional data resolution, I/O interlocking via `HAMMER2_CHAIN_IOINPROG`, checksum validation, INITIAL zero/new buffer handling, and last-unlock data release.
- `hammer2_chain_base_and_count()` and `hammer2_chain_countbrefs()` abstract parent blockref arrays and synchronize live blockref counts used by create/delete/search logic.
- `hammer2_chain_resize()` reallocates data/indirect/dirent physical storage when size changes, preserving data through modify/COW when needed and dropping old DIO state for caller-provided data rewrites.
- `hammer2_chain_modify()` is the central mutation routine: marks MODIFIED/UPDATE, handles dedup offsets, copy-on-write allocation, overwrite-in-place eligibility for CHECK_NONE data beyond snapshots, emergency-mode modify-in-place fallback, DIO replacement/dirtying, BLKMAPUPD propagation, and flush visibility.
- `hammer2_chain_modify_ip()` couples inode metadata modification with chain modification.
- `hammer2_chain_find()`, `hammer2_base_find()`, and `hammer2_combined_find()` merge in-memory RB-tree chains with on-media blockref arrays for range lookup/iteration.
- `hammer2_chain_get()`, `hammer2_chain_lookup_init()`, `hammer2_chain_lookup_done()`, `hammer2_chain_getparent()`, `hammer2_chain_repparent()`, and `hammer2_chain_repchange()` handle materializing media blockrefs into chains, safe parent acquisition despite lock-order reversal, and parent tracking across deletion/reparenting.
- `hammer2_chain_lookup()`, `hammer2_chain_next()`, and `hammer2_chain_scan()` provide key lookup, iteration, and raw blockref scans, including direct-data inode shortcut handling, deleted-chain skipping, upward/downward indirect traversal, and generation-race retries.
- `hammer2_chain_create()` creates or reconnects chains under a parent, inherits or enforces check methods, creates indirect blocks when blockref arrays are full, sets PFSROOT flags, inserts into parent RB/live state, and marks new chains modified.
- `hammer2_chain_create_indirect()` creates indirect/freemap-node blocks, chooses a keyspace, moves qualifying child blockrefs/chains into the new node while preserving original blockrefs when required, and returns the proper parent for the pending insert.
- `hammer2_chain_rename()`, `hammer2_chain_rename_obref()`, `_hammer2_chain_delete_helper()`, `hammer2_chain_delete()`, and `hammer2_chain_delete_obref()` move or remove chains from live RB trees and blockref arrays, preserving old blockrefs for indirect-maintenance moves and marking permanent deletions for flush/destroy.
- `hammer2_chain_indirect_maintenance()` deletes empty indirect blocks or collapses sparse indirect blocks back into the parent when the parent has room, with reptrack handoff for in-progress parent lookups.
- `hammer2_chain_indkey_freemap()`, `hammer2_chain_indkey_file()`, and `hammer2_chain_indkey_dir()` compute new indirect key/keybits for freemap, file data, inode index, and directory hash spaces.
- `hammer2_base_delete()` and `hammer2_base_insert()` maintain sorted parent blockref arrays, live-zero hints, BLKMAPPED/BLKMAPUPD flags, `leaf_count`, and embedded inode/data statistics.
- `hammer2_chain_setcheck()` and `hammer2_chain_testcheck()` generate and validate configured check modes: none/disabled, iSCSI CRC32, xxHash64, SHA192, and freemap CRC.
- `hammer2_characterize_failed_chain()` rate-limits checksum failure reporting and attempts to trace the failed chain back to an inode, PFS, and device.
- `hammer2_chain_inode_find()` locates inode chains by checking live inode structures first, then the inode index radix tree, validating the returned inode number.
- `hammer2_chain_bulksnap()` and `hammer2_chain_bulkdrop()` create/free a volume-root snapshot chain used by bulk scans.
- `hammer2_chain_dirent_test()` matches inode or dirent chains against names, including embedded short dirent names.
- `hammer2_dump_chain()` recursively prints chain topology for debugging.

## Dependencies
Relies on HAMMER2 structures and helpers from `hammer2.h`, DragonFly mutex/spin/lock/buf primitives, kernel allocation APIs, HAMMER2 freemap allocation/adjustment, flusher integration, inode lookup helpers, volume data, I/O layer, CRC/hash routines (`hammer2_icrc32`, `XXH64`, SHA256), rate-limited console printing, and many HAMMER2 flags/constants.

## Behavior/Risks
- This is a high-risk core metadata module. It coordinates COW, snapshots, dedup, freemap allocation, cached chain topology, and flush propagation.
- Lock ordering is delicate. Parent/child traversal uses top-down chain locks, bottom-up spinlock nesting for some ref/drop paths, nonblocking parent acquisition, and reptrack structures to survive deletion/reparent races.
- `hammer2_chain_modify()` has intentionally unsafe emergency-mode modify-in-place paths that can corrupt related snapshots; console warnings are rate-limited.
- Lookups and scans must reconcile on-media blockrefs with modified in-memory chains; generation checks and retry loops guard races, with max-loop panics for runaway corruption or logic bugs.
- Incorrect BLKMAPPED/BLKMAPUPD/UPDATE handling can leak chains, lose parent blockref updates, or leave dirty in-memory inode chains invisible to flush.
- Checksum validation is skipped for `NOTTESTED` and disabled/none modes; failed checks set chain errors and can prevent safe traversal by other modules such as bulkfree.
