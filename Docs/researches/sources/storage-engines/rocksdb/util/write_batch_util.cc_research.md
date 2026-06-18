# sources/storage-engines/rocksdb/util/write_batch_util.cc

## Purpose

Implements a helper for extracting the set of column-family ids referenced by a `WriteBatch`.

## APIs, control flow, and state

`CollectColumnFamilyIdsFromWriteBatch` asserts the output vector is non-null, clears it, constructs a `ColumnFamilyCollector`, iterates the batch, and on success copies each collected column-family id into the output vector. On iteration failure it returns the error and leaves the output vector empty or partially untouched after clear.

## Dependencies and integration

It depends on `util/write_batch_util.h`, which provides `ColumnFamilyCollector` and write-batch declarations. `udt_util.cc` uses this helper to decide whether a WAL batch contains column families with timestamp-size inconsistencies.

## Risks and test signals

The function depends entirely on `WriteBatch::Iterate` and collector coverage for all record types. It does not sort or deduplicate beyond collector behavior. UDT reconciliation tests indirectly exercise it by building batches with several CF ids and checking consistency decisions.
