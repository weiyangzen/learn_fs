# sources/storage-engines/rocksdb/utilities/secondary_index/secondary_index_mixin.h

Purpose: template mixin that adds secondary-index maintenance to transaction-like write APIs by intercepting puts, entity puts, deletes, and single deletes.

Important APIs/types: overrides tracked/untracked `Put`, `PutEntity`, `Delete`, `SingleDelete`, and SliceParts variants. `Merge` and `MergeUntracked` return not supported. `IndexData` records an applicable `SecondaryIndex`, the previous primary column value, and an optional updated primary column value produced by the index. `PerformWithSavePoint()` wraps mutations so failures roll back to a transaction save point.

Control flow and state: put paths lock/read existing primary entity with `GetEntityForUpdate`, remove old secondary entries, let applicable indices update primary column values, write the primary entry with `assume_tracked`, then add secondary entries. Delete paths read existing columns, remove secondary entries, then perform primary delete/single-delete. Secondary keys are finalized prefix plus primary key; secondary values are optional and default to empty.

Dependencies and integration: depends on RocksDB transaction methods supplied by `Txn`, wide-column helpers, `SecondaryIndex` public interface, and `SecondaryIndexHelper`. It is the core write-side bridge used by TransactionDB options carrying secondary indices.

Risks and test signals: secondary-entry remove uses `SingleDelete`, so correctness depends on one existing version per secondary key under transaction semantics. All existing secondary entries for a row are removed/recreated even if unchanged. Merge is not supported. Tests for FAISS cover put/entity insertion, but update/delete behavior needs separate coverage.
