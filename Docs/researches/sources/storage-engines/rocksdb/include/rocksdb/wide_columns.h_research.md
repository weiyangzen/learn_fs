<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/wide_columns.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/wide_columns.h

Purpose: Defines public data structures for RocksDB wide-column entities: individual named columns, non-owning column collections used for writes, and self-contained/pinnable result storage used for reads.

Important APIs/types/functions: `WideColumn`, `WideColumns`, `kDefaultWideColumnName`, `kNoWideColumns`, `PinnableWideColumns`, equality/inequality operators, and stream output are the main elements. `PinnableWideColumns` provides `SetPlainValue`, `SetWideColumnValue`, `Reset`, move construction/assignment, `columns`, and `serialized_size`.

Control flow: `WideColumn` forwards constructor inputs into non-owning `Slice` members. `PinnableWideColumns` either copies, pins, or moves a serialized value into a `PinnableSlice`, then builds an index of `WideColumn` views over that storage. Plain values become one anonymous default column; serialized wide-column values are parsed by `CreateIndexForWideColumns`.

State and persistence behavior: `WideColumn` owns no bytes and depends on caller-managed backing storage. `PinnableWideColumns` owns or pins `value_` and stores `columns_` slices into that buffer. `unresolved_blob_column_indices_` tracks internal blob-index-backed columns for DB internals.

Dependencies and integration points: Depends on `Slice`, `Status`, `PinnableSlice`, `Cleanable`, `DBImpl`, and column-family APIs using `PutEntity`/`GetEntity`. It is referenced by `WriteBatch`, `WriteBatchBase`, and `WriteBatchWithIndex`.

Risks and edge cases: Passing temporary strings to `WideColumn` is unsafe because slices outlive the temporaries. Move logic must rebuild column indexes when pinned data changes address. Parse failures in `SetWideColumnValue` reset the object to avoid exposing invalid column slices.

Test signals: Wide-column tests should verify non-owning lifetime expectations, plain value conversion to the default column, serialized entity parsing, move assignment after copy/pin/move sources, equality/output formatting, and blob-column resolution paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/wide_columns.h -->
