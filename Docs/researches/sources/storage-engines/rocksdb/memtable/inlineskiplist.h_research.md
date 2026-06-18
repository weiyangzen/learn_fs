# sources/storage-engines/rocksdb/memtable/inlineskiplist.h

## Purpose
`inlineskiplist.h` defines `InlineSkipList<Comparator>`, RocksDB's memory-efficient skiplist optimized for memtable keys allocated through the skiplist itself. Compared with `SkipList<const char*>`, it stores key bytes inline with the node and places higher-level next pointers before the node object, reducing per-node pointer overhead and improving cache locality.

## Important APIs, Types, and Functions
- `AllocateKey(size_t)` allocates node plus inline key storage and returns the key payload address.
- `Insert`, `InsertConcurrently`, `InsertWithHint`, and `InsertWithHintConcurrently` link allocated keys into the list. The concurrent variants use CAS.
- `Splice` caches predecessor/successor brackets at each level for insertion hints and finger searches.
- `Node` stores `Atomic<Node*> next_[1]`; levels above zero are addressed with negative offsets before the node. `StashHeight` temporarily stores the randomly chosen height in `next_[0]` before insertion.
- `Iterator` supports forward/backward iteration, seek, seek-for-prev, random seek, and validation variants.
- `MultiGet()` performs batched sorted-key lookup using `FindGreaterOrEqualWithFinger`.
- `ApproximateNumEntries()` estimates range cardinality using higher skiplist levels.
- `TEST_Validate()` checks structural ordering across levels.

## Control Flow
Allocation chooses a random height, allocates aligned memory for extra next pointers, the node, and key bytes, and stashes the height. Insertion unstashes height, raises `max_height_` if needed, validates or recomputes the splice, then links the node level by level. Non-concurrent insertion uses release stores after no-barrier next initialization. Concurrent insertion uses CAS on predecessor next pointers and recomputes stale brackets after failed CAS.

Search starts at the current top height and descends while comparing decoded keys. Validation variants can detect out-of-order neighboring nodes and call a key validation callback. `MultiGet()` expects query keys sorted in non-decreasing comparator order; it reuses a stack-allocated `Splice` as a finger so each next search starts near the previous result.

## State and Persistence Behavior
Nodes are never removed until the allocator is destroyed. Node contents other than links are immutable after publication. `max_height_` is relaxed because stale values only affect efficiency. No persistent state exists in the file; it is an in-memory index over memtable records.

## Dependencies and Integration Points
The template depends on RocksDB `Allocator`, `Slice`, `Random`, atomic wrappers, `PREFETCH`, and sync points. `skiplistrep.cc` wraps it as the default `SkipListRep`. Tests in `inlineskiplist_test.cc` exercise basic operations, insertion hints, concurrent insertion, validation, and `MultiGet`.

## Risks and Test Signals
Correctness depends on comparator support for `DecodedType` and `decode_key`. Hint ownership matters: concurrent hint insertion requires no concurrent calls using the same hint, and heap-allocated hints returned by `AllocateSpliceOnHeap()` must be freed by the caller. `MultiGet()` requires sorted keys; unsorted batches could violate finger preconditions. The validation hooks expose corruption as `Status::Corruption`, while normal non-validation paths assert ordering in debug builds. Tests cover duplicate MultiGet key regression, concurrent MultiGet, and concurrent reads/inserts.
