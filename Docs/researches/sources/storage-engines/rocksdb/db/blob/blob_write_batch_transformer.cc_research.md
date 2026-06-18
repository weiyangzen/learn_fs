# sources/storage-engines/rocksdb/db/blob/blob_write_batch_transformer.cc

## Purpose

This implementation transforms an input `WriteBatch` into an output batch that stores eligible large values directly in blob files and replaces them with `BlobIndex` records. It is the direct-write bridge between the write batch layer and `BlobFilePartitionManager`. Non-qualifying operations are copied through unchanged so callers can use the transformed batch only when at least one value was separated.

It also handles wide-column entities by rewriting eligible columns into V2 serialized wide-column entities containing blob references, while preserving rollback accounting for blob records already appended to blob files.

## Important APIs, Types, and Functions

- `BlobWriteBatchTransformer::TransformBatch(...)`: static entry point. Clears the output batch, iterates the input batch through the handler, reports whether any value was transformed, and returns used partition managers and rollback info.
- `MaybePreprocessWideColumns(...)`: shared helper for sorted wide-column arrays. It selects a wide-column partition, writes each column meeting `min_blob_size`, decodes the generated blob index, and serializes either V2 blob-bearing entities or inline entities.
- `PutCF(...)`: direct-write path for ordinary puts. It caches per-CF settings and manager lookups, writes qualifying values with `BlobFilePartitionManager::WriteBlob`, records `RollbackInfo`, encodes a `BlobIndex`, and appends `PutBlobIndex` to the output batch.
- `PutEntityCF(...)`: deserializes V2 entities, rejects pre-existing blob references, rewrites large columns through `MaybePreprocessWideColumns`, or passes the original serialized entity through.
- `TimedPutCF`, deletes, range deletes, merges, existing blob indexes, log data, and transaction markers are pass-through handlers implemented with `WriteBatchInternal`.

## Control Flow

`TransformBatch` constructs a handler and calls `input_batch->Iterate(&transformer)`. Each callback writes to `output_batch_`. If no callback transforms data, `has_transformed_` remains false and callers can ignore the output batch.

For a `PutCF`, the handler refreshes cached CF settings/partition manager when the CF ID changes. It passes through when no manager exists, direct write is disabled, or the value is below `min_blob_size`. Otherwise it writes the blob, tracks the manager and exact file/count/byte rollback tuple, encodes a `BlobIndex`, sets `has_transformed_`, and emits a blob-index put.

For a `PutEntityCF`, the handler similarly caches CF state, passes through when direct write is unavailable, deserializes the entity as V2, rejects entities that already contain blob references, then calls the wide-column preprocessing helper. If no column qualifies, the original serialized entity is preserved; if any column qualifies, the rewritten entity is emitted.

All transaction-control records are reproduced in the output batch, so transformed batches preserve prepare/commit/rollback/noop structure.

## State and Persistence Behavior

The transformer itself is per-batch and transient, but it causes persistent side effects before the DB write batch has necessarily committed: qualifying values are appended to blob files via `BlobFilePartitionManager::WriteBlob`. Because those appends may outlive a later write failure, the transformer collects `RollbackInfo` with partition manager, file number, blob count, and byte count so callers can account abandoned writes as initial garbage.

The class caches the last CF settings and partition manager to avoid repeated provider lookups for consecutive entries. It also stores `used_managers_` so callers can flush or sync blob file managers after transformation. `blob_index_buf_` is reused across puts to reduce allocation.

## Dependencies

The implementation depends on `BlobFilePartitionManager`, `BlobIndex`, `BlobLogRecord`, wide-column serialization, `WriteBatchInternal`, compression settings from `BlobDirectWriteSettings`, and `WriteBatch::Handler` callback ordering. It uses `UNLIKELY` for the unsupported pre-serialized blob-reference path.

## Integration Points

This code is called from write paths that enable blob direct write. It consumes provider callbacks so the DB layer can supply per-column-family blob settings and partition managers. Its output is a normal `WriteBatch` containing inline entries plus blob index entries, making it compatible with the rest of write batch processing, WAL/transaction markers, memtable insertion, and recovery semantics.

The wide-column path integrates with entity serialization: it accepts already sorted columns and emits V2 entities when blob references are present. It intentionally rejects user-supplied/pre-serialized entities with blob references because those references would not be covered by the current batch's blob lifetime tracking.

## Risks

- Blob writes happen before the transformed batch is durable, so rollback accounting must remain exact or garbage statistics and blob GC can become inaccurate.
- `MaybePreprocessWideColumns` may write some blobs and then fail during a later blob write, blob-index decode, or serialization; callers depend on partial rollback info being returned.
- Pre-existing blob references in entities are rejected to avoid stale references; relaxing that rule would require lifetime tracking outside this transformer.
- The output batch is meaningful only when `transformed` is true. Callers must use the original batch when false because pass-through output is still produced during iteration but is documented as ignorable only in the no-transform case.
- CF setting caching assumes provider results are stable for the duration of one batch transformation.

## Test Signals

Useful verification signals include transformed flag behavior, output batch contents (`PutBlobIndex` for qualifying puts and `PutEntitySerialized` V2 for qualifying entities), correct pass-through for deletes/merges/timed puts/transaction markers, used manager collection, rollback byte counts using `BlobLogRecord::kHeaderSize + key.size() + blob_size`, rejection of V2 entities with existing blob references, and successful reads of transformed values through normal DB paths.
