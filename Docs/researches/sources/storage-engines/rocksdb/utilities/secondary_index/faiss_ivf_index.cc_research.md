# sources/storage-engines/rocksdb/utilities/secondary_index/faiss_ivf_index.cc

Purpose: implements `FaissIVFIndex`, a RocksDB secondary index that stores FAISS IVF inverted-list entries in a RocksDB secondary column family and queries them through a `SecondaryIndexIterator`.

Important APIs/types: helper functions serialize FAISS list labels as varint signed integers. `FaissIVFIndex::Adapter` implements `faiss::InvertedLists` with iterator-based reads and `add_entry` writes into a string context. `IteratorAdapter` seeks a secondary iterator to one list label, validates values as FAISS codes, maps transient FAISS ids to primary keys, and feeds code pointers to FAISS search. Public methods set/get primary and secondary column families, transform primary column values into list labels, build secondary key prefixes, encode secondary values, and perform KNN search.

Control flow and state: construction replaces the FAISS index's inverted lists with the RocksDB adapter and forces `parallel_mode = 0`. On writes, `UpdatePrimaryColumnValue()` assigns the input vector to a coarse list and stores the label as the primary column's indexed value; `GetSecondaryValue()` calls `index_->add_core()` to generate the code stored under `label + primary_key`. On search, FAISS probes lists using `SearchParametersIVF::inverted_list_context`, which lets the adapter enumerate RocksDB entries on demand.

Dependencies and integration: depends on FAISS `IndexIVF`, `InvertedLists`, RocksDB `SecondaryIndex`, `SecondaryIndexIterator`, `ConvertSliceToFloats`, `autovector`, and varint coding. Integrated through `SecondaryIndexMixin`/TransactionDB secondary-index hooks.

Risks and test signals: code assumes vector slices are exactly `index_->d` floats and secondary values are exactly `code_size`. Iterator value pointers point into RocksDB iterator-owned storage and must remain valid until FAISS consumes them. Exceptions from FAISS/iterator code are converted to RocksDB status. Tests compare against a native FAISS baseline and cover invalid KNN arguments.
