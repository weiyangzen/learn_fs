# sources/storage-engines/rocksdb/memtable/hash_linklist_rep.cc

## Purpose
`hash_linklist_rep.cc` implements the `hash_linkedlist` memtable representation. It partitions memtable entries by a transformed user-key prefix, stores sparse buckets compactly as a single node or sorted linked list, and promotes dense buckets to per-bucket skiplists after a configurable threshold.

## Important APIs, Types, and Functions
- `BucketHeader` stores a bucket `next` pointer and relaxed `num_entries`; `next == this` marks a promoted skiplist bucket.
- `SkipListBucketHeader` embeds a `BucketHeader` plus `SkipList<const char*, KeyComparator&>`.
- `Node` stores an atomic `next_` pointer and inline `key[1]` payload.
- `HashLinkListRep` implements `Allocate`, `Insert`, `Contains`, `Get`, `GetIterator`, and `GetDynamicPrefixIterator`.
- Iterator variants are `FullListIterator` for total-order snapshots, `LinkListIterator` for a single linked bucket, `DynamicIterator` for prefix-seek-time bucket selection, and `EmptyIterator`.
- `HashLinkListRepFactory` registers options: `bucket_count`, `threshold`, `huge_page_size`, `logging_threshold`, and `log_when_flash`.

## Control Flow
`Insert()` hashes `Transform(ExtractUserKey(internal_key))` to select a bucket. Empty buckets store the node directly. A one-entry bucket is converted to a `BucketHeader` before inserting more nodes so readers never confuse a modified node with a header. Linked buckets are kept sorted by memtable key. Once `num_entries == threshold_use_skiplist_`, a new `SkipListBucketHeader` is allocated, all existing list entries plus the new node are inserted into the skiplist, and the bucket pointer is release-stored to the new header. Already-promoted buckets increment the count and insert into the skiplist.

`Get()` selects the prefix bucket, then either seeks the sorted linked list or the skiplist and calls the supplied callback until it stops. `GetIterator()` builds a new full `MemtableSkipList` containing all entries across all buckets, optionally recording bucket-size histogram logging. `GetDynamicPrefixIterator()` returns an iterator that chooses a bucket only when `Seek()` is called.

## State and Persistence Behavior
All data is in allocator-owned memory and lives for the memtable lifetime. Bucket array entries are atomics. Release/acquire stores and loads protect publication of nodes and headers, and old nodes/headers are never modified destructively during representation upgrades. There is no disk persistence; persistence happens later through memtable flush.

## Dependencies and Integration Points
The implementation depends on `db/memtable.h`, `memtable/skiplist.h`, `SliceTransform`, `GetSliceRangedNPHash`, `HistogramImpl`, and option registration. It integrates through `NewHashLinkListRepFactory`, which is selected by RocksDB options or the memtablerep benchmark. It requires a prefix extractor; without a valid transform, prefix hashing cannot work.

## Risks and Test Signals
The representation assumes single-threaded `Insert()`; `num_entries` increments are relaxed and not atomic RMW. Dynamic prefix iteration does not support total-order operations like `SeekToFirst`, `SeekToLast`, or reverse traversal for linked buckets. Full iteration is expensive because it materializes a new global skiplist. `ApproximateMemoryUsage()` returns zero because arena allocations are accounted elsewhere. Risks are indirectly covered by RocksDB memtable tests and benchmark coverage; this specific file has no listed dedicated unit test in the subset.
