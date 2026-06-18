# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dbuf.c

## Role

`dbuf.c` implements ZFS DMU buffer (`dmu_buf_impl_t`) lifecycle, caching, lookup, reading, dirtying, syncing, eviction, prefetch, user callbacks, and ARC integration. It is the central bridge between dnodes, block pointers, ARC buffers, zio reads/writes, transaction groups, and the public `dmu_buf_*` operations used elsewhere.

## Major Responsibilities

- Maintains the global dbuf hash table keyed by `(objset, object, level, blkid)` using CityHash.
- Maintains two dbuf caches:
  - `DB_DBUF_METADATA_CACHE`: metadata dbufs retained for administrative traversal speed.
  - `DB_DBUF_CACHE`: regular LRU-style cache with low/mid/high water eviction.
- Creates, finds, holds, releases, and destroys dbufs.
- Reads dbufs from ARC/zio, including holes, bonus buffers, spill blocks, encrypted data, compressed/raw buffers, and freed-in-flight cases.
- Tracks dirty records per txg and links dirty records into dnode or parent indirect dirty lists.
- Writes dirty dbufs during syncing and updates block pointers, fill counts, accounting, and DDT prefetch/remap state.
- Provides async prefetch through indirect block chains.
- Handles ZIL `dmu_sync()` override states through dirty-record block pointer overrides.
- Manages user data attached to dbufs and eviction callbacks.

## Key Data and State

- `dbuf_hash_table`: global hash buckets plus mutex striping for locating live dbufs.
- `dbuf_caches[DB_CACHE_MAX]`: multilist-backed caches plus byte refcounts.
- `dbuf_cache_max_bytes`, `dbuf_metadata_cache_max_bytes`: tunable cache sizing, defaulting to ARC fractions.
- `dbuf_cache_evict_thread`: background eviction worker for the regular dbuf cache.
- `db_state`: important states include `DB_UNCACHED`, `DB_READ`, `DB_FILL`, `DB_CACHED`, `DB_NOFILL`, `DB_EVICTING`.
- `db_dirtycnt`, `db_last_dirty`, `db_data_pending`: txg dirty bookkeeping and sync-in-progress state.
- Dirty records are leaf or indirect variants:
  - Leaf records hold ARC/data buffers and override/nopwrite/raw encryption parameters.
  - Indirect records own child dirty-record lists and a mutex.

## Important Functions

- `dbuf_init()` / `dbuf_fini()` initialize hash table, kmem cache, multilist caches, taskq, and eviction thread.
- `dbuf_find()`, `dbuf_hash_insert()`, `dbuf_hash_remove()` implement identity lookup and uniqueness.
- `dbuf_create()` constructs a dbuf, inserts non-bonus dbufs into the hash and dnode AVL tree, and holds parent/dnode references.
- `dbuf_hold_impl()` finds or creates a dbuf, removes it from cache if needed, increments holds, and handles pending sync data copies.
- `dbuf_rele_and_unlock()` decrements holds and either destroys, caches, freezes, or evicts user data depending on state.
- `dbuf_destroy()` tears down ARC buffers, bonus allocations, cache membership, AVL/hash membership, parent holds, and dnode holds.
- `dbuf_read()` and `dbuf_read_impl()` cover cached, uncached, in-flight, hole, bonus, encrypted, compressed, and async ARC read paths.
- `dbuf_dirty()` creates dirty records, handles copy-on-write isolation, updates dnode dirty context, links parent dirty records, and prefetches DDT entries for overwritten dedup blocks.
- `dbuf_undirty()` removes a dirty record for a txg and may destroy the dbuf if its txg hold was the final hold.
- `dbuf_free_range()` clears or destroys level-0 dbufs in a freed range, including in-flight read/fill handling.
- `dbuf_sync_list()`, `dbuf_sync_indirect()`, `dbuf_sync_leaf()`, and `dbuf_write()` drive txg sync writeout.
- `dbuf_write_ready()`, `dbuf_write_done()`, and related callbacks update block pointers, fill counts, accounting, and dirty-record cleanup.
- `dbuf_prefetch_impl()` walks cached or on-disk indirect ancestors and issues speculative ARC reads.
- `dbuf_remap()` and helpers update block pointers after device removal remapping.

## Interactions

- Uses ARC for allocation, loaning, reading, writing, freezing, releasing, raw/encrypted/compressed buffer handling, and eviction notification.
- Uses zio for synchronous/asynchronous reads and writes.
- Uses dnode locks and structures for object metadata, indirect hierarchy, dirty lists, bonus/spill buffers, and object size.
- Uses DSL dataset/pool code for dirty accounting, block birth/kill accounting, dataset block remap accounting, and sync context checks.
- Uses DDT prefetch on dedup overwrites.
- Uses SPA feature state for embedded data, device removal, encryption, and ARC sizing.

## Notable Invariants and Locking

- Hash-table lock order is `DBUF_HASH_MUTEX > db_mtx`.
- Parent block pointer access is protected by either parent `db_rwlock` or dataset `ds_bp_rwlock`.
- `dn_struct_rwlock` protects dnode structure changes while walking block hierarchies.
- Held dbufs cannot be evicted; unheld cacheable dbufs may enter one of the dbuf caches.
- Bonus dbufs are not placed in the global dbuf hash table.
- Dirty data may require just-in-time copies so older txgs sync stable bytes while newer txgs mutate current dbuf data.
- `dbuf_rele_and_unlock()` carefully avoids recursive eviction stacks by accepting an `evicting` flag.
- Encrypted dnode blocks require authentication/decryption before dependent encrypted data is returned.

## Research Notes

This file is the core DMU buffer state machine. Most subtle behavior comes from maintaining consistency between dbuf holds, ARC buffer ownership, dirty txg records, dnode hierarchy locks, and block pointer updates across open and syncing contexts. Any change here can affect read correctness, txg isolation, ZIL sync, encryption authentication, dedup accounting, device-removal remap, or memory pressure behavior.
