# sources/storage-engines/wiredtiger/test/cppsuite/src/component/metrics_monitor.cpp

Purpose: Samples runtime and postrun metrics, validates configured bounds, and exports selected performance metrics.

Important APIs/types/functions: `get_stat_field` maps configured stat names to WT stat ids. `metrics_monitor::get_stat` reads one statistic from a statistics cursor. `load` constructs stat checkers for cache size, database size, history-store inserts, and checkpoint-cleanup pages, then opens a `statistics:` cursor. `do_work` checks runtime stats. `finish` records saved metrics and validates postrun min/max limits.

Control flow: after base component load, subconfigs define which stats are runtime/postrun/save. Runtime checks happen each loop; final checks happen once in `finish`.

State and persistence: owns a session/cursor and vector of `statistics` objects. Saved metrics are accumulated in `metrics_writer` and written later to JSON.

Dependencies/integration: depends on `connection_manager`, `statistics` subclasses, `database`, constants, and WiredTiger stat ids.

Risks and test signals: only recognized stat names can be mapped by `get_stat_field`. Postrun failures log detailed min/max/actual and call `testutil_die`; runtime failures fail immediately.
