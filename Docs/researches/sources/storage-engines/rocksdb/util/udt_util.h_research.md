# sources/storage-engines/rocksdb/util/udt_util.h

## Purpose

Declares the UDT WAL-record and recovery utilities used when timestamp-size metadata in persisted logs/manifests must be reconciled with current column-family settings.

## APIs, control flow, and state

`UserDefinedTimestampSizeRecord` stores `(cf_id, timestamp_size)` pairs, encodes them as fixed32/fixed16 records, decodes records whose total length is a multiple of six bytes, and formats debug output. `TimestampRecoveryHandler` is a `WriteBatch::Handler` that rewrites batch entries into a new batch according to running and recorded timestamp-size maps. `TimestampSizeConsistencyMode` selects strict verification or best-effort reconciliation. Additional APIs validate UDT option transitions, convert U64 cutoff timestamps to/from `full_history_ts_low`, and add timestamps to range bounds.

## Dependencies and integration

The header depends on wide-column serialization, write-batch internals, `rocksdb/write_batch.h`, `rocksdb/status.h`, coding helpers, and hash maps. It is on the WAL recovery and manifest-opening path.

## Risks and test signals

The major risk is accepting an unsafe comparator or timestamp-size transition. The comments document permitted recovery cases and policy constraints. `udt_util_test.cc` covers batch reconciliation and comparator option validation, while decode/encode has less direct coverage in this subset.
