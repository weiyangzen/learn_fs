# sources/storage-engines/wiredtiger/src/cache/shared_dsk.c

## Purpose

Implements the shared disk-image cache used by disaggregated standby nodes to share immutable page disk images across checkpoints. It hashes disk addresses plus file IDs to cache entries, reference-counts shared images, updates cache/image accounting, and frees images when no page references remain.

## Important APIs, Types, And Functions

`__wt_shared_dsk_cache_get` looks up an address and file ID, increments the entry refcount on hit, and returns a `WT_SHARED_DSK_ITEM`. `__wt_shared_dsk_cache_put` inserts a disk image or detects a collision with an existing entry; on insert, ownership of the caller's `data` moves to the cache, while on collision/error the caller retains ownership. `__wt_shared_dsk_cache_release` decrements refcount and removes/frees the entry on last release. `__wt_shared_dsk_cache_init` allocates hash buckets and bucket-lock array. `__wti_shared_dsk_cache_destroy` frees all buckets, images, and locks. `__shared_dsk_cache_verbose` formats address-level verbose logs.

The file uses `WT_SHARED_DSK_CACHE`, `WT_SHARED_DSK_ITEM`, `WT_PAGE_BLOCK_META`, `WT_PAGE_HEADER`, per-bucket TAILQs, spin locks, file ID `S2BT(session)->id`, CityHash, and cache statistic/accounting helpers.

## Control Flow

Get computes `hash = city64(addr)`, maps it to `bucket` and `lock_idx`, locks that stripe, scans the bucket for same address size, file ID, and bytes, increments `ref_count` if found, unlocks, and records hit/miss stats. Put preallocates and fills a wrapper with data pointer, data size, copied block metadata, file ID, address bytes, and refcount 1 before taking the bucket lock. Under lock it scans for an existing item; on collision it increments the existing item refcount, returns it, and frees only the unused wrapper. If no collision exists, it inserts the wrapper at the bucket head, transfers data ownership, and increments shared-disk and image cache accounting.

Release recomputes the bucket from the stored address, decrements refcount under the lock, and either leaves the item in place or removes it. The last-release path updates accounting after unlocking, overwrites/frees the disk image bytes, and frees the wrapper. Init sizes the lock array to `min(hash_size, 2000)`, initializes all queues and locks, and publishes hash-size stats. Destroy walks every bucket and frees remaining items without requiring refcount-zero.

## State And Persistence Behavior

The cache stores in-memory copies of disk page images and block metadata; it does not persist new data. Keys are physical disk addresses scoped by btree file ID, so entries represent immutable storage content. Refcounts model sharing by page instances. Cache byte/image counters are updated symmetrically on insert and final release, making this cache visible to broader eviction and cache accounting.

## Dependencies And Integration Points

Initialized from `__wt_cache_create` for disaggregated standby roles and destroyed from `__wt_cache_destroy`. The code integrates with page read/reconciliation paths that can attach shared disk items to pages, the cache accounting layer (`__wt_cache_shared_dsk_inmem_incr`, `__wt_evict_shared_dsk_cache_bytes_decr`, `__wt_cache_image_incr/decr`), connection stats, verbose cross-checkpoint-cache logging, and diagnostic counters for max bucket walk/refcount.

## Risks

Ownership transfer in `put` is easy to misuse: callers must free their data only when `insertedp` is false or an error occurs. `addr_size` is stored in a `uint8_t`, so callers must respect address size bounds. Destroy frees all entries regardless of refcount, so it must only run when no pages can still reference shared items. Hash collisions are handled by full address/file comparison, but long buckets can affect performance; diagnostic max-bucket-walk counters help identify this. Accounting must remain symmetric or cache shutdown/statistics will report leaked image bytes.

## Test Signals

Useful coverage includes get-miss/get-hit behavior, duplicate put collision preserving caller ownership, refcount increment/decrement and final removal, separate entries for same address in different file IDs, statistics hit/miss/hash-size updates, image byte accounting across insert/release, destroy with populated buckets, and disaggregated standby startup/teardown with verbose cross-checkpoint cache logging.
