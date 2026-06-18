# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_log_spacemap.c

This file implements log space maps, an optimization for random-write/random-free workloads that batches metaslab space-map changes into pool-wide per-TXG log space maps and later flushes selected metaslabs.

Key behavior:
- On disk, `DMU_POOL_LOG_SPACEMAP_ZAP` maps TXG keys to log space-map object IDs.
- Each top-level vdev can persist per-metaslab unflushed TXGs in `VDEV_TOP_ZAP_MS_UNFLUSHED_PHYS_TXGS`.
- In memory, `spa_sm_logs_by_txg` tracks log maps by TXG with metaslab and block counts, `spa_metaslabs_by_flushed` orders metaslabs by `ms_unflushed_txg`, and `spa_log_summary` aggregates counts for fast flush estimation.
- Tunables control log space-map block size, unflushed memory limits, log block limits, summary length, minimum metaslabs to flush, historical TXGs used for incoming-rate estimation, and test behavior at export.
- `spa_log_sm_set_blocklimit()` derives a capped block limit from total metaslab count and tunables.
- `spa_log_summary_verify_counts()` cross-checks summary counters against AVL state and aggregate SPA counters when debug log-spacemap checks are enabled.
- `spa_log_summary_decrement_mscount()` and `spa_log_summary_decrement_blkcount()` maintain summary state when metaslabs flush or old logs are destroyed, including device-removal and flush-all corner cases.
- `spa_estimate_incoming_log_blocks()` averages recent log-map block counts, excluding the current syncing TXG.
- `spa_estimate_metaslabs_to_flush()` projects incoming blocks into future TXGs and uses the summary to choose a per-TXG flush count that keeps log blocks below the limit.
- `spa_flush_metaslabs()` runs only in sync pass 1, ensures a syncing log map exists, then flushes oldest metaslabs until block and memory heuristics are satisfied or all logs are requested for export.
- `spa_sync_close_syncing_log_sm()` records the current log map’s block count, updates aggregate block counts and summary, closes the map, and clears flush-all state after export flushing.
- `spa_cleanup_old_sm_logs()` destroys obsolete log maps whose TXG is older than the oldest unflushed metaslab TXG and removes their ZAP entries.
- `spa_generate_syncing_log_sm()` creates the ZAP on first use, activates `SPA_FEATURE_LOG_SPACEMAP`, allocates a new space map for the current TXG, adds in-memory tracking, and opens it with broad address range support.
- Import path: `spa_ld_unflushed_txgs()` loads per-metaslab unflushed TXGs, `spa_ld_log_sm_metadata()` loads and validates log metadata, `spa_ld_log_sm_data()` replays log entries into metaslab unflushed alloc/free trees, and `spa_ld_log_spacemaps()` orchestrates the full load.

Important invariants:
- Flush heuristics operate in sync pass 1 and depend on ordered metaslab and log-map trees.
- Log replay skips entries for removed vdevs and ignores entries older than a metaslab’s persisted unflushed TXG.
- Import failure paths still recompute metaslab accounting enough for clean teardown.
