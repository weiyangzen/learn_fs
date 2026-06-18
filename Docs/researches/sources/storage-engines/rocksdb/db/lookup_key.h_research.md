<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/lookup_key.h -->
# sources/storage-engines/rocksdb/db/lookup_key.h

## Purpose
Declares `LookupKey`, the compact lookup-key helper used by `DBImpl::Get()` and memtable/table lookup paths. It packages a user key, optional user-defined timestamp, and snapshot sequence number into the length-prefixed memtable key and internal-key forms expected by RocksDB's internal comparators.

## Important APIs, Types, And Functions
The constructor `LookupKey(const Slice& _user_key, SequenceNumber sequence, const Slice* ts = nullptr)` is declared here and implemented in `dbformat.cc`. Public accessors are `memtable_key()`, `internal_key()`, and `user_key()`. `memtable_key()` returns the full length-prefixed buffer; `internal_key()` skips the varint length and returns `userkey|tag`; `user_key()` strips the final 8-byte internal tag and returns the user-key portion, including user-defined timestamp bytes when enabled.

The object stores three internal pointers (`start_`, `kstart_`, `end_`) and a 200-byte inline buffer. The destructor frees heap storage only when the key did not fit in `space_`. Copying and assignment are disabled.

## Control Flow
Callers construct a `LookupKey` for a user key and sequence/snapshot. The constructor encodes `klength` as varint32, appends user key plus timestamp when applicable, and appends a packed sequence/type tag. Memtable code passes `memtable_key().data()` to memtable reps for efficient seek and uses `internal_key()` for comparator ordering.

## State And Persistence Behavior
`LookupKey` is stack-oriented transient state. It persists nothing, but its exact byte layout is a cross-module contract with memtable entries, internal iterators, and comparators. The inline buffer avoids allocation for short keys; long keys allocate dynamically and are released by the destructor.

## Dependencies And Integration Points
Depends on `rocksdb/slice.h` and `rocksdb/types.h`. It is consumed by `memtable.cc` `Get`, `MultiGet`, `Update`, `UpdateCallback`, and merge-count paths, and by DB get/read flows that need a consistent internal-key representation.

## Risks And Edge Cases
Returned slices point into the `LookupKey` object and become invalid when it is destroyed. The `user_key()` accessor includes timestamp bytes by design, so callers that need timestamp-stripped keys must use timestamp-aware helpers. Layout changes must remain compatible with memtable entry encoding and `InternalKeyComparator`.

## Test Signals
Coverage is indirect through memtable get/update/multiget tests, comparator/internal-key tests, and DB read paths with and without user-defined timestamps. Bugs typically surface as missed memtable hits, incorrect snapshot visibility, or comparator-order violations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/lookup_key.h -->
