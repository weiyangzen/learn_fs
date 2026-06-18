# sources/storage-engines/rocksdb/util/set_comparator.h

## Purpose

Defines `SetComparator`, a small adapter that lets `Slice` values be ordered in STL ordered containers using a RocksDB user comparator. It defaults to `BytewiseComparator()` when no comparator is supplied.

## APIs, control flow, and state

The only public API is the constructor pair plus `bool operator()(const Slice&, const Slice&) const`. The operator delegates to `Comparator::Compare` and returns true for strictly negative comparison. The object stores a raw `const Comparator*`; it does not own or persist comparator state.

## Dependencies and integration

It depends on `rocksdb/comparator.h` and is intended for components that need `std::set<Slice, SetComparator>` semantics consistent with DB key ordering. Its main integration constraint is comparator lifetime: callers must keep the comparator alive for every set operation.

## Risks and test signals

There is no direct test in this subset. Risks are dangling comparator pointers and comparator inconsistency violating strict weak ordering. Null construction is safe through the bytewise fallback, but non-null custom comparators must remain valid.
