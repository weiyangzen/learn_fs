# sources/storage-engines/rocksdb/memtable/hash_skiplist_rep.cc

## Purpose
`hash_skiplist_rep.cc` implements the `prefix_hash` memtable representation. It maps transformed user-key prefixes into hash buckets, each lazily initialized as a regular `SkipList<const char*, KeyComparator&>`.

## Important APIs, Types, and Functions
- `HashSkipListRep` implements the `MemTableRep` interface for insert, point/prefix lookup, total iteration, and dynamic prefix iteration.
- `Bucket` is an alias for `SkipList<const char*, const MemTableRep::KeyComparator&>`.
- `GetHash()` uses `MurmurHash(prefix) % bucket_size_`.
- `GetInitializedBucket()` allocates a bucket skiplist from the memtable allocator and publishes it in `buckets_`.
- `Iterator` wraps a bucket or a materialized full-list skiplist. It may own the list when used for full iteration.
- `DynamicIterator` recomputes the prefix bucket on `Seek()`.
- `HashSkipListRepFactory` registers `bucket_count`, `skiplist_height`, and `branching_factor`, with nickname `prefix_hash`.

## Control Flow
`Insert()` extracts the user key from the encoded memtable key, transforms it, lazily initializes the hashed bucket, and inserts the key into that bucket skiplist. `Contains()` performs the same bucket selection and delegates to `Bucket::Contains`. `Get()` uses the lookup key user prefix, seeks within the bucket by the full memtable key, and invokes the callback over matching entries until it returns false.

For total-order iteration, `GetIterator()` allocates a new arena and full skiplist, scans every non-null bucket from first to last, inserts all entries into the global list, and returns an owning iterator over that list. Dynamic prefix iteration avoids this cost but is only meaningful after seeking a specific prefix.

## State and Persistence Behavior
Buckets are atomic pointers stored in allocator memory. Bucket creation is published with a release store and read with acquire loads. There is no deletion of bucket skiplists during memtable lifetime. The file itself persists nothing; entries are in-memory memtable records that later flush through RocksDB.

## Dependencies and Integration Points
This file uses `memtable/skiplist.h`, `SliceTransform`, `MurmurHash`, option metadata, and `MemTableRepFactory`. It is selected through `NewHashSkipListRepFactory` or configuration strings. It integrates with `memtablerep_bench.cc`, which names it as `hashskiplist` or `prefix_hash`.

## Risks and Test Signals
`GetInitializedBucket()` is not protected by CAS, so concurrent first insertion into the same empty bucket could allocate and publish races unless higher-level insert serialization applies. `SeekForPrev()` in the bucket iterator asserts false, so reverse prefix iteration is unsupported. Full iteration has O(number of entries) rebuild cost and an extra arena. `ApproximateMemoryUsage()` returns zero because allocator-level accounting owns memory usage. Coverage is mostly through generic memtable tests and benchmark selection rather than a dedicated test file in this subset.
