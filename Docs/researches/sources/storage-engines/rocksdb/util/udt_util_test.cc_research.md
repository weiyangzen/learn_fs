# sources/storage-engines/rocksdb/util/udt_util_test.cc

## Purpose

Tests UDT timestamp-size reconciliation for WAL write batches and validates allowed/disallowed UDT option transitions.

## APIs, control flow, and state

The fixture builds write batches containing put, delete, single-delete, range-delete, merge, blob-index, timed-put, and entity records for configured CF timestamp sizes. `KeyCollector` iterates resulting batches and verifies CF ids, keys, values, entity deserialization, and write times. Tests cover all-consistent maps, inconsistent dropped CFs, involved-only consistency, timestamp stripping, timestamp padding, copying dropped CF entries during reconciliation, and unrecoverable nonzero-size mismatch. Comparator tests cover enabling `.u64ts`, disabling it, unchanged comparator persist-flag behavior, and invalid comparator changes. A final test verifies U64 cutoff-to-full-history conversion.

## Dependencies and integration

It depends on DB format timestamp helpers, write-batch internals, wide columns, test comparators, and test utilities. It uses in-memory batches and does not open a DB.

## Risks and test signals

Strong signals include preserved sequence numbers and counts, exact key timestamp deltas, retained values/entity content, and expected `InvalidArgument` failures. The suite does not deeply exercise `UserDefinedTimestampSizeRecord` decode corruption paths.
