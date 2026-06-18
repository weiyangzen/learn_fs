# sources/storage-engines/wiredtiger/src/cursor/cur_stat.c

## Purpose
Implements WiredTiger statistics cursors for connection, session, file, table, index, colgroup, layered, tiered, and size-only statistics. It snapshots or aggregates stats into `WT_CURSOR_STAT` and exposes each statistic by integer key with description, printable value, and numeric value.

## Important APIs, types, and functions
`__wt_curstat_open` validates statistics configuration, allocates `WT_CURSOR_STAT`, saves cursor config for refresh, initializes the first snapshot, and installs cursor methods. `__wt_curstat_init` dispatches `statistics:` URIs to connection, session, file, table, index, colgroup, layered, or tiered initializers. `__curstat_get_key`, `__curstat_get_value`, `__curstat_set_keyv`, `__curstat_next`, `__curstat_prev`, and `__curstat_search` implement cursor traversal and access. `__wt_curstat_size_local`, `__wt_curstat_size_disagg`, and `__curstat_file_size` provide a fast size-only path. `__wt_curstat_dsrc_final` finalizes data-source stats layout.

## Control flow
Open parses the `statistics` configuration, enforcing compatibility with connection stats flags and rejecting incompatible combinations such as `size` plus `clear`. It sets key format `i` and value format `SSq`. Traversal lazily refreshes if `notinitialized` is set, then uses `stats_base`, `stats_count`, and optional `next_set` callbacks to walk one or more statistic sets. Search validates the requested statistic ID range and returns the corresponding offset. Reset marks the cursor for reinitialization and clears session stats immediately for `statistics:session`.

## State, persistence, and dependencies
Statistics are copied or aggregated into the cursor union (`conn_stats`, `dsrc_stats`, or `session_stats`) and are not persistent user data. The cursor may clear live connection/data-source/session counters when `WT_STAT_CLEAR` is set. File size may come from local filesystem/block-manager size or from disaggregated checkpoint metadata. Layered-table stats aggregate ingest and stable constituent tables, with followers reading the most recent stable checkpoint name.

## Integration points
This file integrates with generated statistic descriptors, connection/stat flag configuration, btree stat initialization, schema stats helpers for tables/indices/colgroups, block manager file sizing, disaggregated checkpoint sizing, layered table handles, and the standard cursor API. It asserts data-source statistics are not available before recovery completes.

## Risks and test signals
Risk areas include correct stat-key base/count arithmetic, config compatibility, clearing behavior, size-only fast path falling back safely, dhandle release in layered and file initialization, and refresh semantics after reset. Tests should cover all URI dispatches, raw and non-raw key/value access, next/prev/search boundaries, `statistics=(all|fast|size|clear|cache_walk|tree_walk)` combinations, local missing files, disaggregated checkpoint sizes, and layered follower checkpoint lookup.
