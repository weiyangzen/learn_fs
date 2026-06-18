# sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/table.rs

## Purpose
`table.rs` implements table-boundary split checking. When enabled, it tries to split a region at TiDB table-prefix boundaries so a region spanning multiple tables can be separated.

## Important APIs, Types, And Functions
`Checker` stores the first table prefix, an optional split key, and policy. `TableCheckObserver` adds this checker when `Config::split_region_on_table` is enabled. Helpers include `last_key_of_region`, `to_encoded_table_prefix`, `is_table_key`, and `is_same_table`.

## Control Flow
`TableCheckObserver::add_checker` first skips if table splitting is disabled or the region start/end are in the same table. It reads the last key in `CF_WRITE` within the encoded region bounds. Based on how encoded start and last/end keys compare with TiDB's table prefix, it either skips non-table ranges, precomputes a split key, records the starting table prefix for scan-time detection, or adds a default scanner for short keys.

The scan `Checker::on_kv` converts the data key to origin key. If it has no first table prefix yet, the first table key can become a split key. If it has a prefix and sees a key from another table, it extracts that table prefix and stops. `split_keys` returns the precomputed or detected encoded table-prefix key once.

## State And Persistence Behavior
State is only per split-check run. It reads engine state through a write-CF iterator but does not mutate or persist data. Split execution is delegated to the surrounding split-check runner.

## Dependencies And Integration Points
Uses `engine_traits` iterators over `CF_WRITE`, TiDB table codec constants and prefix extraction, `txn_types::Key`, `KeyBuilder`, and split-check host traits. It is registered by default after size and keys observers, with table splitting gated by configuration.

## Risks
The logic assumes TiDB table key encoding and only inspects `CF_WRITE` for the last key. Non-table data, short keys, and ranges crossing table/non-table areas have special branches that can skip or force scans. Prefix comparison uses the first encoded table-prefix bytes, so any table key format change would require updates. Errors from iterator creation are logged and cause table splitting to be skipped.

## Test Signals
Tests verify `last_key_of_region` across open and bounded ranges and table-check behavior for ranges spanning table data, starting inside a table, ending before table data, crossing non-table prefixes, and skipping same-table ranges.
