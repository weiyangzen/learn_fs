# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/compact_log.rs

Purpose: Implements raft log compaction and entry-cache eviction for raftstore-v2, including periodic leader decisions, compact-log admin proposals, apply results, raft-engine GC, and tombstone tablet destruction coordination.

Important APIs/types/functions: `CompactLogContext` tracks skipped ticks, approximate log size, last applying index, last compacted index, tombstone tablet indexes waiting for persistence, and an atomic persisted tablet index. `PeerFsmDelegate::on_compact_log_tick` and `on_entry_cache_evict` handle ticks. `Peer::maybe_propose_compact_log` decides compact indexes from applied, first/last, replicated, alive-cache, count/size thresholds, force flag, and skipped tick policy. `propose_compact_log` serializes the admin command. `Apply::apply_compact_log` returns `CompactLogResult`. Peer methods record tombstone tablets, remove them when persisted, handle apply compaction results, advance persisted apply index cleanup, and calculate `compact_log_index`.

Control flow: Leaders periodically schedule compact-log ticks, compact local caches, and propose a compact-log admin request when thresholds are met. Apply returns a compact result without mutating much itself. The peer apply-result handler updates truncated state, persists apply state in `state_changes`, cancels snapshot generation for compacted indexes, schedules raft-engine GC only after persisted apply allows deletion, and adjusts approximate log size. Persisted-apply advancement deletes older raft states and schedules tablet destruction callbacks after safe persistence.

State and persistence behavior: Persistent state changes include apply truncated state, apply-state records, raft-engine GC commands, and cleanup of historical region/apply/flush state records. Tombstone tablet destruction is delayed until replacement tablet indexes are persisted, preventing removal of data still referenced by inflight apply.

Dependencies and integration points: It integrates raftstore config thresholds/metrics, raft-engine `RaftLogBatch`, tablet worker tasks, write-task persisted callbacks, entry storage, merge context, transfer leader cache warmup, and admin command routing.

Risks: Index arithmetic is delicate, including the inherited `compact_idx -= 1` behavior. Assertions require compact indexes below last applying index and no pending tombstone tablets before destroy. Cache warmup can defer compaction. Approximate log size scaling divides by `total_cnt`, so invariants must ensure progress. The TODO notes missing unit tests for compact-log message integrity.

Test signals: Failpoint `maybe_propose_compact_log` exists. Assertions and metrics expose behavior, but local tests are absent. Integration should cover forced compaction, threshold skipping, merge max compact index, persisted-apply cleanup, snapshot cases, and tombstone tablet lifecycle.
