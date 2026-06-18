# sources/storage-engines/tikv/tests/failpoints/cases/test_async_fetch.rs

Purpose: tests raft log async fetch, entry cache retention, and log compaction coordination when peers lag, restart, change leadership, or are removed.

Important APIs and functions: tests include `test_node_async_fetch`, `test_persist_delay_block_log_compaction`, `test_node_async_fetch_remove_peer`, `test_node_async_fetch_leader_change`, and `test_node_compact_entry_cache`. They use `new_node_cluster`, PD peer operations, `RaftApplyState` from `CF_RAFT`, `check_compacted`, and failpoints such as `on_async_fetch_return`, `worker_async_fetch_raft_log`, `worker_gc_raft_log`, `apply_pending_snapshot`, and `before_region_gen_snap`.

Control flow: each test configures raft log GC thresholds and entry cache lifetime, creates lagging peers by stopping nodes or isolating traffic, writes enough entries to trigger async fetch or compaction, pauses internal workers, then resumes and validates catch-up.

State and persistence: reads persisted raft apply truncated state from the raft CF and validates KV replication after restarts/removals. Compaction is expected to wait when persist is delayed.

Dependencies and integration: integrates raftstore cluster simulation, PD client peer management, engine traits, and fail-rs.

Risks and test signals: timing sleeps and failpoint ordering are sensitive. Signals include successful lagging-peer recovery, no premature log GC, and retained cache for learners.
