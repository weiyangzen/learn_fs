# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_log_spacemap.h

This header declares pool-wide log spacemap state and helpers for batching metaslab allocation/free deltas before flushing them back to individual metaslab spacemaps.

Core definitions:
- `DIV_ROUND_UP` local helper is defined if absent.
- `log_summary_entry_t` tracks a start TXG, remaining metaslabs to flush, block count, and list linkage.
- `spa_unflushed_stats_t` tracks memory used by unflushed trees plus block-limit and block-count heuristics.
- `spa_log_sm_t` records a log spacemap object, its TXG, block count, metaslabs flushed in that TXG, and AVL linkage by TXG.

Public API surface:
- Load/generate/flush/close log spacemaps, clean old logs, compute/set block limits, query block and memory usage.
- Decrement/increment metaslab counts for log spacemap and log summary accounting.
- Add flushed metaslabs to summaries, decrement summary block counts, and query flush-all requests.
- Tunable `zfs_keep_log_spacemaps_at_export`.

Risk-sensitive invariants:
- Log spacemaps introduce unflushed allocator deltas; metaslab load/sync/flush code must not double-apply or lose them.
- Summary counts determine when old log spacemap records can be cleaned.
- Memory and block heuristics affect when accumulated unflushed state is forced back to metaslab spacemaps.
