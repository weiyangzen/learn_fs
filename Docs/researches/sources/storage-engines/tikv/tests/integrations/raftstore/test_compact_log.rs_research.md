# sources/storage-engines/tikv/tests/integrations/raftstore/test_compact_log.rs

Purpose: tests raft log garbage collection by entry count, repeated compaction, size limit, and reserve-max-ticks behavior.

Important APIs and functions: helper tests record each engine's `RaftApplyState.truncated_state` via `keys::apply_state_key(1)`, write many keys, and use `check_compacted` to compare before/after truncation. Config knobs include `raft_log_gc_count_limit`, `raft_log_gc_threshold`, `raft_log_gc_size_limit`, `raft_log_gc_tick_interval`, and `raft_log_reserve_max_ticks`.

Control flow: scenarios start node clusters, write an initial key to establish state, then write enough entries or bytes to cross a specific compaction criterion. Size-limit coverage stops one node to avoid checking lagging state. Reserve-max-ticks sets limits high enough that normal thresholds are not reached, then asserts tick-based reserve policy still compacts.

State and persistence: persisted raft apply state and truncated log index/term are the primary state. Key/value reads ensure writes are applied before compaction checks. Lagging or stopped nodes are intentionally excluded where appropriate.

Dependencies and integration points: uses raftstore log GC, raft apply state encoding, engine traits, `ReadableSize`/`ReadableDuration`, and `test_raftstore` compaction helpers.

Risks: timing sleeps can be flaky if log GC ticks are delayed. Compaction amount is implementation-dependent, so tests mainly compare state advancement, not exact indexes. Size-limit behavior depends on encoded raft log sizes.

Test signals: truncated state advances only after configured thresholds/ticks are reached, repeated compaction can advance at least twice the configured limit, and key reads continue to succeed after log GC.
