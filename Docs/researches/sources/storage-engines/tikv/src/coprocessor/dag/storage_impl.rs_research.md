# sources/storage-engines/tikv/src/coprocessor/dag/storage_impl.rs

Purpose: implements `tidb_query_common::storage::Storage` on top of TiKV's `Store` abstraction so query executors can scan MVCC data.

Important APIs/types: `TikvStorage<S>` stores the underlying `Store`, an optional active scanner, accumulated CF statistics, and `NewerTsCheckState` for cacheability. `begin_scan` drains stats from the prior scanner, preserves any newer-ts detection, builds raw-key lower/upper bounds, and creates a new TiKV scanner. `scan_next_entry` returns owned key/value/optional commit-ts entries. `get_entry` performs point gets through `incremental_get_entry`. `met_uncacheable_data` reports whether newer-ts data was observed. `collect_statistics` merges store/scanner stats into the destination and resets the backlog.

State and persistence: no writes are persisted; scanner state, statistics, and cacheability state are request-local. Dependencies include `txn_types::Key`, TiKV `Scanner/Store/Statistics`, and query-engine `OwnedKvPairEntry`.

Integration points: used by DAG, checksum, and analyze scanning paths. Risks include `scan_next_entry` relying on `begin_scan` having been called, correct conversion from raw query ranges to `txn_types::Key`, and accurate newer-ts reporting for coprocessor cache decisions. Tests are indirect through DAG/analyze/checksum endpoint behavior.
