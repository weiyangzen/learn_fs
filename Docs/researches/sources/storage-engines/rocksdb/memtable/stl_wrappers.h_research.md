# sources/storage-engines/rocksdb/memtable/stl_wrappers.h

## Purpose
`stl_wrappers.h` provides a small adapter for using RocksDB memtable key comparators with STL containers and algorithms.

## Important APIs and Types
- `stl_wrappers::Base` stores a reference to `MemTableRep::KeyComparator`.
- `stl_wrappers::Compare` derives privately from `Base` and implements `bool operator()(const char* a, const char* b) const` as `compare_(a, b) < 0`.

## Control Flow
There is no complex control flow. `Compare` is constructed with a memtable comparator and can be passed to algorithms like `std::sort` to order encoded memtable keys consistently with RocksDB internal ordering.

## State and Persistence Behavior
The wrapper stores only a comparator reference. It does not own data and has no persistence.

## Dependencies and Integration Points
The header includes comparator, memtable rep, slice, and coding headers. In this subset, `vectorrep.cc` uses `stl_wrappers::Compare(compare_)` when lazily sorting its vector-backed bucket.

## Risks and Test Signals
Lifetime matters: the referenced comparator must outlive any STL comparator object using it. Ordering must be strict and consistent with the memtable's encoded key format. There is no dedicated test; coverage comes through vector memtable behavior and any STL sort/search users.
