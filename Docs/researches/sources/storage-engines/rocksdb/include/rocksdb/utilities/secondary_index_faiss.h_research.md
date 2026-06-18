# sources/storage-engines/rocksdb/include/rocksdb/utilities/secondary_index_faiss.h

## Purpose
Experimental `SecondaryIndex` implementation backed by a FAISS IVF vector index for nearest-neighbor lookup over embedding columns.

## Important APIs, Types, And Functions
`FaissIVFIndex` owns `faiss::IndexIVF`, implements all `SecondaryIndex` methods, and adds `FindKNearestNeighbors`. `ConvertFloatsToSlice` and `ConvertSliceToFloats` convert between contiguous float spans and RocksDB `Slice`.

## Control Flow, State, And Persistence
Transactional maintenance maps embeddings into secondary index entries. KNN search validates target dimension and positive neighbors/probes, uses the associated `SecondaryIndexIterator`, probes FAISS inverted lists, and returns primary keys with distances. FAISS index and adapter are in-memory; secondary entries persist in RocksDB.

## Dependencies And Integration Points
Depends on FAISS `IndexIVF`, `SecondaryIndex`, `Slice`, and `Status`. Integrates with transaction secondary-index maintenance and vector search.

## Risks And Edge Cases
Requires a correctly trained FAISS IVF index. Embedding slices must be exactly `dim * sizeof(float)` and depend on binary float layout. Search can return fewer than requested neighbors. Column-family handles are non-owning runtime pointers.

## Test Signals
Cover construction preconditions, embedding conversion, dimension validation, index maintenance, KNN result order/distances, invalid probe/neighbor counts, and exhausted candidate lists.
