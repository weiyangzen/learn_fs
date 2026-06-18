<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/write_batch_base.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/write_batch_base.h

Purpose: Defines the abstract write-batch interface shared by `WriteBatch` and indexed or transactional batch implementations. It gives DB-facing code a common mutation surface independent of concrete batch storage.

Important APIs/types/functions: `WriteBatchBase` declares pure virtual `Put`, timestamped `Put`, `TimedPut`, `PutEntity`, attribute-group `PutEntity`, `Merge`, timestamped `Merge`, `Delete`, timestamped `Delete`, `SingleDelete`, timestamped `SingleDelete`, `DeleteRange`, timestamped `DeleteRange`, `PutLogData`, `Clear`, `GetWriteBatch`, savepoint methods, and `SetMaxBytes`. `SliceParts` overloads are virtual with out-of-line default implementations.

Control flow: Concrete subclasses implement the primary `Slice` APIs. The base class supplies common overload structure so clients can call through one type. `GetWriteBatch` bridges abstract implementations back to a concrete serialized `WriteBatch` for DB write submission.

State and persistence behavior: The base class owns no state. Persistence semantics are inherited from implementations: a concrete `WriteBatch` serializes operations directly, while `WriteBatchWithIndex` additionally tracks searchable transient indexes.

Dependencies and integration points: Depends on `attribute_groups.h`, `rocksdb_namespace.h`, `Slice`, `Status`, `ColumnFamilyHandle`, `WriteBatch`, and `SliceParts`. It is used throughout APIs that accept generic batches or transaction write buffers.

Risks and edge cases: The comment contains a spelling typo, but the behavioral risk is API drift: new write record types must be added here and implemented by every subclass. Feature availability differs by subclass, so callers must handle `NotSupported` statuses from indexed or specialized batches.

Test signals: Cross-implementation tests should exercise the same operation set through `WriteBatchBase*`, including unsupported operations, savepoints, max-byte limits, `SliceParts` defaults, and conversion via `GetWriteBatch`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/write_batch_base.h -->
