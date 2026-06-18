# sources/storage-engines/rocksdb/db/blob/blob_write_batch_transformer.h

## Purpose

This header declares the public contract for direct-write blob batch transformation. It defines the per-column-family settings required to decide whether a write should be separated into blob files, provider callback types for settings and partition managers, and the `BlobWriteBatchTransformer` handler class that rewrites `WriteBatch` contents.

The header is intentionally narrow: it exposes enough for DB write paths to invoke transformation and clean up side effects, while leaving blob writing and partition selection to `BlobFilePartitionManager`.

## Important APIs, Types, and Functions

- `BlobDirectWriteSettings`: settings snapshot with `enable_blob_direct_write`, `min_blob_size`, `compression_type`, `compression_opts`, raw `Cache* blob_cache`, and `PrepopulateBlobCache`.
- `BlobDirectWriteSettingsProvider`: callback from CF ID to settings.
- `BlobPartitionManagerProvider`: callback from CF ID to `BlobFilePartitionManager*`.
- `BlobWriteBatchTransformer::RollbackInfo`: records `partition_mgr`, `file_number`, appended record `count`, and appended `bytes` for failed transformed writes.
- `MaybePreprocessWideColumns(...)`: static helper for callers that need direct-write processing of wide-column data outside a full batch handler.
- `TransformBatch(...)`: static full-batch API with optional `used_managers` and `rollback_infos` outputs.
- `WriteBatch::Handler` overrides: put, timed put, entity put, delete, single delete, range delete, merge, existing blob index, log data, and transaction markers.
- `HasTransformed()`: reports whether at least one value was rewritten to a blob index.

## Control Flow

The intended call flow is provider setup, `TransformBatch`, then conditional use of the output batch. `TransformBatch` drives the handler callbacks internally, so most callers do not instantiate the handler directly. During callbacks, the private cached CF ID, settings, and partition manager avoid repeated provider lookups.

The class has two transformation surfaces: ordinary key/value puts and wide-column entities. Ordinary puts are rewritten when the value size crosses the CF's minimum threshold. Wide-column entities are parsed and selectively rewritten per column, producing a V2 entity only when necessary.

## State and Persistence Behavior

The header documents that transformation can append blob records before the final batch succeeds. `RollbackInfo` is therefore part of the contract: even on failure, partial blob writes should be observable to callers so they can account them as garbage. `used_managers` similarly exposes which partition managers received data and may need follow-up flush/sync work.

`BlobDirectWriteSettings::blob_cache` is a raw pointer because it is owned by `ColumnFamilyOptions` and expected to outlive settings snapshots. This avoids reference-count overhead in hot put paths but makes lifetime expectations explicit.

## Dependencies

The header depends on RocksDB public option and write-batch types (`advanced_options.h`, `compression_type.h`, `options.h`, `slice.h`, `status.h`, `write_batch.h`) plus `util/hash_containers.h`. It forward-declares `BlobFilePartitionManager` and `Cache` to reduce compile coupling.

## Integration Points

DB write code supplies the two provider callbacks from column-family metadata. The transformed output batch integrates with `WriteBatchInternal`, memtable insertion, WAL/transaction handling, and blob GC accounting. Wide-column integration depends on callers passing sorted `WideColumns`, as documented by `MaybePreprocessWideColumns`.

## Risks

- Provider callbacks and raw cache pointers encode lifetime assumptions that must remain true across write path refactors.
- The header contract says `output_batch` is empty/ignorable when no values qualify, so callers need to respect `transformed`.
- The rollback vector is optional, but callers that skip it cannot precisely account abandoned blob records after transformation failure.
- `MaybePreprocessWideColumns` requires sorted columns; unsorted input can produce serialized entities that violate wide-column ordering assumptions.

## Test Signals

Header-level behavior is validated by implementation and DB tests that check direct-write blob indexes, wide-column entity reads, rollback/garbage accounting, prepopulate cache settings, compression propagation, and pass-through of non-transforming write batch records. API compatibility signals include successful compilation of write path callers using providers, `RollbackInfo`, and all handler overrides.
