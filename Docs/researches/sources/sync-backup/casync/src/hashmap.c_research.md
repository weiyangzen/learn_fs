# sources/sync-backup/casync/src/hashmap.c

## Purpose

`hashmap.c` is a systemd-derived open-addressed Robin Hood hashmap implementation with three public container shapes: `Hashmap` key/value maps, `OrderedHashmap` maps that preserve insertion order, and `Set` key-only containers. It provides allocation, lookup, insertion, replacement, removal, iteration, merge/move/copy, string-vector extraction, and set convenience helpers.

## Important APIs, Types, and Functions

The file defines bucket entry structs for plain maps, ordered maps, and sets. `HashmapBase` contains common hash ops, direct or indirect storage, type bits, direct-entry count, mempool flag, and optional debug fields. Direct storage keeps tiny maps allocation-light using bytes embedded in `HashmapBase`; indirect storage uses heap storage for buckets plus DIB bytes and per-table hash key. `hashmap_type_info` records head size, entry size, mempool, and direct bucket capacity per type.

Robin Hood state uses DIB (distance from initial bucket) bytes with sentinel values for overflow, rehash, and free. Special virtual indexes `IDX_PUT` and `IDX_TMP` are swap buckets used during insertion and resize. `IDX_FIRST` and `IDX_NIL` support iteration.

Allocation APIs are `internal_hashmap_new()`, `internal_ordered_hashmap_new()`, `internal_set_new()`, and ensure-allocated variants. Free/clear APIs include `internal_hashmap_free()`, `internal_hashmap_free_free()`, `hashmap_free_free_free()`, `internal_hashmap_clear()`, `internal_hashmap_clear_free()`, and `hashmap_clear_free_free()`.

Core helpers include `bucket_hash()`, `get_hash_key()`, `bucket_at()`, `dib_raw_ptr()`, `bucket_calculate_dib()`, `bucket_move_entry()`, `base_remove_entry()`, `hashmap_put_robin_hood()`, `hashmap_base_put_boldly()`, `resize_buckets()`, and `base_bucket_scan()`.

Public operations implemented here include `hashmap_put()`, `set_put()`, `hashmap_replace()`, `hashmap_update()`, `internal_hashmap_get()`, `hashmap_get2()`, `internal_hashmap_contains()`, `internal_hashmap_remove()`, `hashmap_remove2()`, `hashmap_remove_and_put()`, `set_remove_and_put()`, `hashmap_remove_and_replace()`, `hashmap_remove_value()`, first/steal-first helpers, size/bucket count, merge, reserve, move, move-one, copy, `internal_hashmap_get_strv()`, `ordered_hashmap_next()`, `set_consume()`, `set_put_strdup()`, and `set_put_strdupv()`.

## Control Flow

Insertion hashes the key with siphash and the container's hash ops, scans for an existing key with Robin Hood early termination, places the new key/value in `IDX_PUT`, resizes if needed, appends insertion-order links for ordered maps, and uses `hashmap_put_robin_hood()` to find or displace buckets until a free slot appears. Resizing upgrades direct storage to indirect storage when necessary, grows bucket storage, generates a new hash key, marks existing entries as needing rehash, then reinserts them using the same Robin Hood logic.

Lookup computes the initial bucket and linearly scans while DIB values show candidates can still exist. If a free bucket appears or the current DIB is smaller than the probe distance, the key cannot be present. Removal uses backward-shift deletion: it removes the bucket from ordered iteration links when applicable, shifts following displaced entries backward until a free or zero-DIB bucket, updates DIB values, marks the final bucket free, and decrements entry count.

Iteration is type-aware. Ordered maps traverse insertion links; plain maps/sets scan storage order. The iterator stores the next key pointer so removal of the current entry during iteration can be tolerated despite backward shifts. With `ENABLE_DEBUG_HASHMAP`, debug counters assert that new insertions or unrelated removals do not happen during iteration.

Move/merge/copy operations reuse lower-level insertion/removal. `internal_hashmap_move()` pre-reserves for the worst case to avoid partial moves on allocation failure. `set_consume()` transfers ownership of a heap value into a set and frees it if it already existed or insertion failed without needing the value.

## State and Persistence Behavior

Container state is in heap or mempool-allocated objects. Direct storage stores buckets and DIBs in the base object. Indirect storage stores heap memory containing all buckets followed by DIB bytes and an independent hash key. A process-global `shared_hash_key` is used for all tiny direct-storage maps; larger maps get randomized keys from `random_bytes()`. Debug builds maintain a global linked list protected by a mutex for GDB inspection.

No filesystem persistence exists. Ownership behavior depends on the free variant: plain free keeps keys/values, free_free frees values, free_free_free frees both keys and values for plain maps; set freeing through `set_free_free()` is implemented through the shared internal paths.

## Dependencies and Integration Points

The implementation depends on `hashmap.h`, `hash-funcs.h`, `set.h`, `mempool.h`, `list.h` in debug builds, siphash, random byte generation, allocation helpers, and utility macros from `util.h`. `gc.c` uses `Set` with custom chunk hash ops. Many casync/systemd utility structures likely depend on this hashmap API.

## Risks and Edge Cases

The implementation is performance-sensitive and invariant-heavy. Bugs in DIB calculation, resize rehashing, virtual swap indexes, or ordered link repair can produce hard-to-debug corruption. The direct-storage shared hash key is acceptable for tiny maps but reduces per-map hash isolation. `is_main_thread()` is hardcoded false, disabling mempool use despite `DEFINE_MEMPOOL()` declarations. Pointer-based trivial compare uses relational pointer comparison. Iteration permits only current-entry removal; debug builds catch more misuse than release builds.

Allocation failure during `hashmap_put()` can leave no insertion, but move operations explicitly pre-reserve to prevent partial migration. `hashmap_remove_and_replace()` has careful compensation for backward shift when removing a duplicate new key; this path deserves regression coverage. `internal_hashmap_get_strv()` assumes `h` is non-null and uses `n_entries(h)` directly. Ordered hashmap insertion links use virtual `IDX_PUT` before the bucket is finalized, so `bucket_move_entry()` must repair links correctly.

## Test Signals

Tests should cover direct-storage and indirect-storage thresholds for map, ordered map, and set; random-heavy insertion/deletion/lookup versus a reference map; ordered iteration after insert/remove/backward shifts; removal during iteration; resize from direct to indirect; DIB overflow via adversarial hash ops; replace/update/remove_and_put/remove_and_replace paths; duplicate set consume freeing; merge/move/copy semantics; `hashmap_get2()` key return; `steal_first` loops; null-map read operations; allocation-failure injection around resize; and debug iterator assertions in `ENABLE_DEBUG_HASHMAP` builds.
