# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/ddt.c

## Role

`ddt.c` implements the ZFS deduplication table manager. It coordinates persistent DDT objects, in-memory DDT entries, DDT statistics/histograms, dedup block pointer construction, ditto-copy policy, repair staging, syncing, loading/unloading, and iteration.

## Major Responsibilities

- Defines DDT backend operations through `ddt_ops`, currently backed by `ddt_zap_ops`.
- Creates, loads, syncs, destroys, looks up, updates, removes, walks, and counts persistent DDT objects.
- Converts between block pointers, DDT keys, and DDT physical entries.
- Maintains dedup histograms and object statistics.
- Tracks in-memory `ddt_entry_t` instances in AVL trees while txgs are open.
- Decides how many ditto copies are needed based on reference count thresholds.
- Supports repair of damaged dedup blocks by rewriting known good copies.
- Syncs modified DDT entries at txg sync time and updates scan state if entry class changes.

## Key Data and State

- `zfs_dedup_prefetch`: tunable enabling prefetch of DDT entries for dedup blocks about to be freed.
- `ddt_ops[DDT_TYPES]`: persistent backend table, currently only ZAP.
- `ddt_class_name[]`: persistent naming for `ditto`, `duplicate`, and `unique` classes.
- Each `ddt_t` owns:
  - `ddt_tree`: in-memory modified/loaded entries.
  - `ddt_repair_tree`: queued repair entries.
  - `ddt_object[type][class]`: persistent object IDs.
  - `ddt_histogram` and `ddt_histogram_cache`.
  - `ddt_object_stats`.
  - checksum selector, SPA pointer, MOS objset pointer, and lock.

## Important Functions

- `ddt_object_create()` creates a backend DDT object, records it in the pool directory, and creates its histogram stat entry.
- `ddt_object_destroy()` removes empty persistent DDT objects and their stats.
- `ddt_object_load()` loads object IDs, histograms, and cached object stats.
- `ddt_object_sync()` writes histogram updates and refreshes cached count/space stats.
- `ddt_bp_create()` builds synthetic dedup block pointers from a DDT key and physical entry.
- `ddt_key_fill()` extracts checksum, size, compression, and crypto properties from a block pointer into a DDT key.
- `ddt_phys_fill()`, `ddt_phys_clear()`, `ddt_phys_addref()`, `ddt_phys_decref()`, `ddt_phys_free()` manage physical copies and refcounts.
- `ddt_phys_select()` locates the DDT physical entry matching a block pointer identity.
- `ddt_stat_generate()`, `ddt_stat_update()`, and histogram helpers maintain logical, physical, referenced, and dedup-space statistics.
- `ddt_lookup()` locates or creates an in-memory entry, serializes concurrent loads with `dde_loading`, and searches all persistent type/class objects.
- `ddt_prefetch()` issues backend prefetches for dedup block entries.
- `ddt_entry_compare()` compares DDT keys as `uint16_t` words for AVL ordering.
- `ddt_create()`, `ddt_load()`, `ddt_unload()` manage per-checksum DDT tables for a SPA.
- `ddt_class_contains()` tests whether a block exists in classes up to a requested maximum.
- `ddt_repair_start()`, `ddt_repair_done()`, `ddt_repair_table()`, `ddt_repair_entry()` implement repair workflow.
- `ddt_sync_entry()` classifies entries, frees zero-ref physical copies, writes/removes persistent entries, and triggers scan handling when class decreases.
- `ddt_sync_table()` drains the in-memory AVL tree and syncs or destroys backend objects.
- `ddt_sync()` wraps DDT sync in an assigned txg and shared scan/repair root zio.
- `ddt_walk()` iterates checksum, type, and class dimensions using a bookmark cursor.

## Interactions

- Uses MOS ZAP entries for persistent DDT object IDs and statistics.
- Uses `zio_free()` to free unreferenced physical dedup copies.
- Uses DSL scan to immediately scan entries whose class decreases.
- Uses ARC/ABD/zio during repair rewrites.
- Uses checksum and compression tables for dedup key encoding and compressed DDT payload encoding.
- Encrypted dedup entries constrain ditto-copy availability because encrypted blocks reserve the last DVA for IV-related data.

## Notable Invariants

- Persistent DDT objects are destroyed only when object count and histograms are empty.
- Loaded entries subtract their old histogram contribution before modifications, then add the new contribution during sync.
- `dde_loading` serializes disk lookup so multiple threads do not load the same DDT entry concurrently.
- DDT physical entries with zero birth must have zero refcount.
- DITTO physical copies may be freed if no longer required by current reference thresholds.
- `ddt_sync()` expects to run in the SPA syncing txg.

## Research Notes

This file owns the logical dedup model, while backend persistence is abstracted through `ddt_ops_t`. The most sensitive areas are class transitions, histogram accounting, repair entry lifetime, encryption-related copy limits, and sync-time removal/update ordering.
