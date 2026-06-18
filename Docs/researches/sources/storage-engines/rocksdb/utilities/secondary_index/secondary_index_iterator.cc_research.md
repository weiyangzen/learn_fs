# sources/storage-engines/rocksdb/utilities/secondary_index/secondary_index_iterator.cc

Purpose: implements `SecondaryIndexIterator`, a prefix-scoped wrapper over a normal RocksDB iterator for scanning one secondary-index key prefix.

Important APIs and control flow: construction stores a `SecondaryIndex` and underlying iterator. `Seek(target)` asks the index to finalize the target prefix, stores it as an owned string, and seeks the underlying iterator to that prefix. `Valid()` requires OK wrapper status, underlying validity, and key prefix match. `key()` strips the prefix from the underlying key, while `value`, `columns`, `timestamp`, `PrepareValue`, `Next`, `Prev`, `status`, and `GetProperty` delegate to the underlying iterator.

State and persistence: iterator state is transient: `prefix_`, `status_`, index pointer, and underlying iterator. It does not write data.

Dependencies and integration: used by FAISS KNN search to enumerate one or more inverted lists and by consumers of public secondary-index APIs. It depends on `SecondaryIndexHelper` for variant conversion.

Risks and test signals: the code has a FIXME that prefix seeking works for `BytewiseComparator` but not arbitrary comparators. `Prev()` can step outside the prefix and then `Valid()` becomes false. Tests exercise forward scans indirectly through FAISS.
