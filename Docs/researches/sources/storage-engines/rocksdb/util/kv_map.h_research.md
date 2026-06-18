# sources/storage-engines/rocksdb/util/kv_map.h

Purpose: defines a comparator-aware STL map alias for key/value strings, useful in tests and utilities that need RocksDB comparator ordering rather than `std::string` byte ordering hardcoded by `std::less`.

Important APIs/types/functions: `stl_wrappers::LessOfComparator` stores a `const Comparator*` defaulting to `BytewiseComparator()` and overloads `operator()` for `std::string` and `Slice`. `stl_wrappers::KVMap` is `std::map<std::string, std::string, LessOfComparator>`.

Control flow: map comparisons wrap both inputs in `Slice` where needed and call `Comparator::Compare`, returning true when the result is negative. Construction of the comparator captures the comparator pointer once.

State and persistence behavior: no persistence. Runtime state is only the comparator pointer stored inside the map comparator and the key/value strings stored by `std::map`.

Dependencies/integration points: depends on `rocksdb/comparator.h`, `rocksdb/slice.h`, and standard map/string. It supports code paths that need STL containers to mimic DB key ordering, especially tests with custom comparators.

Risks: the comparator pointer is non-owning and must outlive the map. Changing the comparator object after keys have been inserted would violate `std::map` ordering assumptions. The include of `util/coding.h` is not used directly in this header.

Test signals: no local test file in this subset directly targets `KVMap`; its confidence comes from consumers that instantiate comparator-aware maps in RocksDB tests and utilities.
