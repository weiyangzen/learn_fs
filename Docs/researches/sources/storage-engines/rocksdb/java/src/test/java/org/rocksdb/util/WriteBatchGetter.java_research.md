# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/WriteBatchGetter.java

Purpose: Test `WriteBatch.Handler` that tracks the latest value for a single target key while iterating a write batch.

Important APIs/types/functions: constructor `WriteBatchGetter(byte[] key)`, `getValue`, overrides for `put`, `merge`, `delete`, `singleDelete`, `putBlobIndex`, and unsupported callbacks.

Control flow and state: each relevant callback compares the event key with the target using `Arrays.equals`. Puts, merges, and blob indexes store the event value; deletes and single deletes set value to null. CF-aware overloads also update `columnFamilyId`, though no getter exposes it. Range deletes, log records, and transaction markers throw `UnsupportedOperationException`.

State and persistence behavior: in-memory reduction over a batch stream; no persistence. Stored `value` references are not copied.

Dependencies and integration points: useful for tests that need batch lookup semantics without opening a DB.

Risks: unsupported callbacks make it unsafe for arbitrary modern write batches containing ranges, logs, or transaction markers. Merge is treated as value replacement, not merge-operator semantics. CF id is private and unused.

Test signals: downstream tests can assert final target value/null after batch iteration.
