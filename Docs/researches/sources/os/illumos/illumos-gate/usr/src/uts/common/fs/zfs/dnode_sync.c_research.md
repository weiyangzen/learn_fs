# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dnode_sync.c

## Purpose

Implements syncing-context dnode writeback and block freeing. It applies pending dnode geometry/type/bonus/spill/maxblkid changes, increases indirection, frees block-pointer ranges recorded by open context, updates used-space accounting, evicts or undirties dbufs when freeing objects, activates large-dnode features, and drives child dbuf sync.

## Main Entry Points

- `dnode_sync()`: primary syncing-context entry for one dirty dnode.
- `dnode_increase_indirection()`: creates a new top indirect level and reparents cached children.
- `dnode_sync_free_range_impl()` / `dnode_sync_free_range()`: free recorded logical block ranges.
- `free_blocks()`, `free_children()`: kill dataset block pointers and recurse through indirect blocks.
- `dnode_sync_free()`: finish freeing an entire dnode.
- `dnode_evict_dbufs()`, `dnode_evict_bonus()`: evict cache state used by sync/free paths.
- `dnode_undirty_dbufs()`: drop dirty records for a dnode being freed.

## Control Flow And State

`dnode_sync()` starts by applying accounting flags and newly allocated dnode physical fields. It consumes txg-indexed pending fields from `dn_next_type`, `dn_next_blksz`, `dn_next_bonuslen`, `dn_next_bonustype`, `dn_next_indblkshift`, `dn_next_maxblkid`, and `dn_next_nblkptr`. Spill blocks are removed if explicitly requested or if the dnode is being freed.

Free ranges recorded in `dn_free_ranges[txgoff]` are walked before being vacated and destroyed. `dnode_sync_free_range_impl()` bounds the range to the persistent `dn_maxblkid`, recurses through indirect blocks, kills leaf block pointers with `dsl_dataset_block_kill()`, preserves hole birth metadata when the `hole_birth` feature is active, and optionally frees indirect blocks immediately when the entire dnode is being removed. For ordinary range frees, indirect blocks are usually left to later dbuf write logic so hole birth times are not lost when frees and writes target the same indirect block in one txg.

If a dnode needs more levels, `dnode_increase_indirection()` reads/releases the new top indirect block, copies old root block pointers into it, zeros the old root pointers, and reparents cached child dbufs to the new indirect. It observes dbuf lock ordering by finding children before holding the new parent's `db_rwlock`.

After pending structural changes and range frees, `dnode_sync()` writes dirty child dbufs with `dbuf_sync_list()`. If the dnode is being freed, `dnode_sync_free()` verifies all used bytes are gone, undirties records, evicts dbufs, zeros the physical dnode slots, frees interior slots, resets in-core type/maxblkid/free state, and releases the dirty hold.

## Dependencies

Depends on dbuf dirty records and sync, dataset deadlist/block-kill accounting, ZIO txg sync flow, ARC released buffers, range trees, dnode dirty state produced by `dnode.c`, SPA features `hole_birth` and `large_dnode`, and user accounting state in objsets.

## Risks

The file mutates persistent block pointers while syncing, so ordering is critical: free ranges must be processed before maxblkid updates, and indirection changes must happen before child dbuf sync. Freeing indirects is intentionally restricted because freeing and rewriting the same indirect block in one txg can otherwise lose hole birth metadata. Raw receive bypasses normal maxblkid truncation to preserve source-side cryptographic hashes. The `range_tree_walk()` plus later `range_tree_vacate()` pattern is deliberate because the callback drops `dn_mtx`.
