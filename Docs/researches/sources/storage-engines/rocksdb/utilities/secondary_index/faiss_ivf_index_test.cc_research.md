# sources/storage-engines/rocksdb/utilities/secondary_index/faiss_ivf_index_test.cc

Purpose: integration tests for `FaissIVFIndex` using TransactionDB secondary indices and FAISS IVF Flat indexes.

Important tests: `Basic` trains an IVF index, writes 1024 embeddings as wide-column entities, verifies secondary column-family keys decode into valid list labels and primary ids, verifies values equal original embeddings for `IndexIVFFlat`, runs KNN searches for original vectors, and checks invalid search arguments. `Compare` trains a RocksDB-backed and native FAISS index on the same data, inserts 4096 vectors, and compares result ids/distances over multiple neighbors/probe counts and query vectors.

Control flow and state: tests create primary/secondary column families manually, set them on the index, and wrap a raw RocksDB iterator in `SecondaryIndexIterator` for KNN. Primary keys are decimal ids, which simplifies parsing returned secondary suffixes.

Dependencies and integration: uses FAISS random/vector/index classes, TransactionDB, secondary-index public headers, RocksDB test harness, and coding utilities.

Risks and test signals: coverage is strong for IVF Flat search equivalence and argument validation, but it does not cover deletes/updates of FAISS-indexed rows or non-flat/code-compressed IVF variants. It assumes bytewise ordering compatible with `SecondaryIndexIterator` prefix seeking.
