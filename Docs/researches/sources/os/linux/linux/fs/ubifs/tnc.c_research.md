# File Research: sources/os/linux/linux/fs/ubifs/tnc.c

Read completely: 3575 lines.

This file implements the UBIFS Tree Node Cache (TNC), the in-memory cache and mutation layer for the UBIFS indexing B-tree. It handles lookups, cached leaf nodes, hash-collision resolution, copy-on-write znode dirtying, insertion, replacement, deletion, range removal, bulk-read discovery, and GC/commit membership queries.

Main entry points include `ubifs_lookup_level0`, `ubifs_tnc_locate`, `ubifs_tnc_get_bu_keys`, `ubifs_tnc_bulk_read`, `ubifs_tnc_lookup_nm`, `ubifs_tnc_lookup_dh`, `ubifs_tnc_add`, `ubifs_tnc_replace`, `ubifs_tnc_add_nm`, `ubifs_tnc_remove`, `ubifs_tnc_remove_nm`, `ubifs_tnc_remove_dh`, `ubifs_tnc_remove_range`, `ubifs_tnc_remove_ino`, `ubifs_tnc_next_ent`, `ubifs_tnc_close`, `is_idx_node_in_tnc`, `ubifs_tnc_has_node`, `ubifs_dirty_idx_node`, and `dbg_check_inode_size`.

Old-index protection: `insert_old_idx_znode`, `ins_clr_old_idx_znode`, and `destroy_old_idx` maintain an RB-tree of old index-node positions that must not be overwritten until a successful commit. This protects recovery by preserving the last complete committed index while dirty znodes are being rewritten.

Copy-on-write mutation: `dirty_cow_znode` and `dirty_cow_bottom_up` ensure any znode being committed is copied before modification. They update dirty and clean znode counters, clear on-flash position fields for dirty branches, add obsolete index dirt, and replace old znodes with copies when `COW_ZNODE` is set.

Leaf node cache: hashed leaf nodes such as directory and xattr entries may be copied into `zbr->leaf` to avoid repeated media reads during collision resolution and readdir-like walks. `lnc_add`, `lnc_add_directly`, `lnc_free`, and `tnc_read_hashed_node` manage this small per-branch cache.

Lookup behavior: `ubifs_lookup_level0` descends the TNC, lazily loading missing znodes, and handles the special case where equivalent hashed keys can live to the left of the nominal search path. `lookup_level0_dirty` performs the same search while dirtying the path for mutation.

Collision handling: `resolve_collision`, `fallible_resolve_collision`, and `resolve_collision_directly` scan left/right among equal hashed keys to match by full name or by exact flash position. Fallible variants tolerate dangling branches during journal replay, where a referenced node may have been garbage-collected before commit.

Reads and bulk reads: `ubifs_tnc_locate` can drop `tnc_mutex` for non-hashed node reads and retries safely if GC may have moved the LEB. Bulk-read helpers collect consecutive data-node zbranches for the same inode and same LEB, then read and validate the combined region while detecting GC races with `gc_seq`.

Insert/update/delete: `tnc_insert` inserts zbranches and splits full znodes, including root splits and parent-key correction. `ubifs_tnc_add` replaces unique-key entries or inserts new ones; `ubifs_tnc_add_nm` handles full-name collision semantics. `tnc_delete` removes leaf branches, collapses empty znodes and single-child roots, and records old index positions as needed.

Removal APIs: single-key, name-qualified, double-hash cookie-qualified, key-range, and whole-inode removal paths all converge on dirtying the affected znode and deleting branches while adding obsolete node dirt. `ubifs_tnc_remove_ino` also walks xattr entries and removes their xattr inodes.

Iteration and GC support: `ubifs_tnc_next_ent` walks directory/xattr entries in key order with collision handling. `lookup_znode`, `is_idx_node_in_tnc`, `is_leaf_node_in_tnc`, `ubifs_tnc_has_node`, and `ubifs_dirty_idx_node` let GC and in-the-gaps commit decide whether on-flash nodes remain part of the current or old index.

Important interactions: journal write paths update TNC after writing nodes; GC uses replace and membership checks while moving nodes; `tnc_commit.c` uses the dirty znode lists and old-index records; `tnc_misc.c` supplies load/read/traversal primitives; `shrink_tnc` may reclaim clean subtrees.

Reliability notes: the TNC is serialized by `c->tnc_mutex`, but selected read paths deliberately race with GC and use sequence checks to retry. Correctness depends on preserving old index nodes until commit completion, updating dirty/clean counters consistently, and clearing leaf-cache entries whenever a branch changes.
