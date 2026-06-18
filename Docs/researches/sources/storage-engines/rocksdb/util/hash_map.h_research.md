# sources/storage-engines/rocksdb/util/hash_map.h

Purpose: small fixed-bucket hash map optimized to reduce allocations by storing collision chains in `autovector` rather than node-based lists.

Important type/API: template `HashMap<K, V, size=128>` provides `Contains(K)`, `Insert(K, const V&)`, `Delete(K)`, and `Get(K)` over an array of `autovector<std::pair<K,V>,1>` buckets.

Control flow: all operations compute `key % size` to pick a bucket and linearly scan with `std::find_if`. `Delete()` replaces the removed element with the last element in the bucket before popping. `Get()` returns `it->second` without checking for missing keys.

State and persistence: in-memory fixed bucket array only. No resizing, hashing object, or persistence.

Dependencies and integration: includes `<algorithm>`, `<array>`, `<utility>`, and `util/autovector.h`. Suitable for small integer-key maps where allocation avoidance matters.

Risks: requires `K` to support `% size` and equality. `Insert()` does not check duplicates, so repeated keys can coexist and `Get/Delete` affect the first found. `Get()` is unsafe for absent keys. Fixed bucket count can degrade badly with poor key distribution.

Test signals: no direct test in this subset.
