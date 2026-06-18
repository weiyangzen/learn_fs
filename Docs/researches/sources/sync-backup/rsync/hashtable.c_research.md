# sources/sync-backup/rsync/hashtable.c

## Purpose

`hashtable.c` provides rsync's compact open-addressed hash table for integer keys plus Bob Jenkins lookup3 hash functions for byte strings. The table is used by hard-link matching, one-file-system deletion bookkeeping, and other places that need fast integer-key lookup without per-node allocation.

## Important APIs, Types, And Functions

Exported functions are `hashtable_create(int size, int key64)`, `hashtable_destroy(struct hashtable *tbl)`, `hashtable_find(struct hashtable *tbl, int64 key, void *data_when_new)`, `hashlittle(const void *key, size_t length)`, and, when 64-bit integers are available, `hashlittle2(const void *key, size_t length)`.

The table stores either `struct ht_int32_node` or `struct ht_int64_node` elements selected by `key64`. Macros from `rsync.h` such as `HT_NODE()` and `HT_KEY()` abstract node access. `HASH_LOAD_LIMIT(size)` grows at 75 percent occupancy. Key value zero is reserved as the empty-slot sentinel, so callers must bias real zero keys before insertion.

## Control Flow

`hashtable_create()` rounds the requested size up to at least 16 and to a power of two, allocates a zeroed node array sized for 32-bit or 64-bit keys, initializes counters, and optionally emits hash debug output. `hashtable_destroy()` frees the node array and table.

`hashtable_find()` rejects zero keys, grows the table when inserting past the load limit, reinserts all non-empty old nodes, then hashes the requested key. For 32-bit keys it uses a Jenkins one-at-a-time style byte hash over the little-endian encoded key. For 64-bit keys it uses a compact Jenkins hashword finalization. Lookup uses linear probing with a power-of-two mask. If the key exists, the node is returned. If an empty slot is found and `data_when_new` is null, it returns null. Otherwise it writes the key, sets `node->data` to `data_when_new`, increments entries, and returns the new node.

`hashlittle()` and `hashlittle2()` are adapted lookup3 routines. They choose fast aligned 32-bit, aligned 16-bit, or byte-at-a-time paths based on pointer alignment and endian configuration, mix 12-byte blocks, handle tail bytes through switch fallthrough, finalize, and force nonzero results using `NON_ZERO_32` or `NON_ZERO_64`.

## State And Persistence

State is entirely heap allocated per table. Node data is caller-owned and is not freed by `hashtable_destroy()`. During growth, nodes are reinserted and data pointer values are preserved, including null data through a temporary sentinel path. Debug logging includes table address, size, and key width.

## Dependencies And Integration Points

The file depends on `rsync.h` allocation wrappers, integer typedefs, endian and size macros, hash-table structs/macros, debug/logging helpers, and cleanup on internal errors. `hlink.c` uses nested 64-bit tables for dev/inode groups and a 32-bit table for prior incremental hard-link groups. `generator.c` uses a 64-bit table to track device ids already accepted during one-file-system deletion.

## Risks

Zero is not a valid key. Callers that forget to offset zero-valued device ids or group ids will hit a fatal internal error. Open addressing performance depends on keeping load under the growth threshold and on good hash distribution. The table never deletes individual keys. Data pointer ownership is external, so destroying a table with allocated node data leaks unless the caller frees nested data first, as `idev_destroy()` does. `hashlittle()` is not cryptographic and should not be used for adversarial integrity checks.

## Test Signals

Tests should insert and find 32-bit and 64-bit keys, verify growth preserves keys and null data, reject zero keys, exercise collision probing, destroy nested caller-owned tables, and compare `hashlittle()`/`hashlittle2()` behavior across aligned and unaligned buffers, short tails from 0 to 12 bytes, and big/little endian builds.
