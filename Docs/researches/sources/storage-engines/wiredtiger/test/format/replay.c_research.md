# sources/storage-engines/wiredtiger/test/format/replay.c

Purpose: implements predictable replay, where operations at a given timestamp are deterministic across runs with the same seeds and data can be compared at matching stable timestamps.

Important APIs and functions: `replay_end_timed_run`, `replay_maximum_committed`, `replay_operation_enabled`, `replay_loop_begin`, `replay_run_begin`, `replay_run_end`, `replay_read_ts`, `replay_prepare_ts`, `replay_commit_ts`, `replay_rollback_ts`, `replay_committed`, `replay_adjust_key`, `replay_rollback`, `replay_stale_read_ts`, and `replay_pause_after_rollback`. Static `replay_pick_timestamp` and `replay_run_reset` manage lane allocation.

Control flow: each replay operation claims a unique timestamp, maps its low bits to a lane, marks the lane in use, seeds per-thread data/extra RNGs from timestamp xor configured seeds, and constrains keys to the same lane. Commits update lane `last_commit_ts`; if global timestamp has advanced more than one lane cycle, the same thread must replay the next timestamp in that lane. Rollbacks retain timestamp/lane and retry. Stable timestamp computation scans in-use lanes and caches the largest safe committed timestamp.

State and persistence: controls `g.timestamp`, `g.timestamp_copy`, `g.stop_timestamp`, `g.replay_start_timestamp`, `g.replay_cached_committed`, `g.replay_calculate_committed`, `g.lanes[]`, and per-thread replay fields. It indirectly determines all persisted data values by seeding RNGs and selecting keys/operations.

Dependencies and integration: used by `ops.c` transaction and key-selection paths, `format_timestamp.c` timestamp advancement, and snapshot retry handling. It requires timestamped transactions and forbids truncate operations in replay mode.

Risks and test signals: any non-replay mutation of `g.timestamp` violates `timestamp_copy` assertions. Lane release/reclaim bugs can permit same-key races or make stable timestamp move incorrectly. Signals include deterministic compare failures, replay assertions, stuck rollback retries, and stale read timestamp detection.
