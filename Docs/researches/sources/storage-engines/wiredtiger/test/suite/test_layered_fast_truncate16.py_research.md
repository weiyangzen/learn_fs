<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate16.py

Purpose: verifies that pending follower truncates are drained correctly into stable storage when a follower steps up to leader, across range shapes, timestamps, mixed per-key histories, and layered removes.

Important APIs/types/functions: class `test_layered_fast_truncate_stepup` uses the fast-truncate mixin, separate `conn_follow/session_follow`, local `populate_on_leader`, `write_kv`, `remove_kv`, `truncate_range`, `assert_visible`, `assert_deleted`, and `assert_keys_gone`. `step_up()` comes from the mixin and calls `disagg_switch_follower_and_leader`.

Control flow: setup creates 1000 stable integer keys at ts=10 and opens a follower. Tests cover stable-only truncates, ranges with follower updates, reinsert after truncate, single/start/end/full/empty ranges, multiple/duplicate/overlapping truncates, snapshot reads before/at/after truncate timestamps, mixed stable and follower-updated keys, empty truncate list step-up, post-step-up writes, ingest keys exactly at bounds, truncates below stable timestamp, and remove/truncate combinations including same timestamp.

State and persistence behavior: follower truncate-list state must be replayed into leader-stable history with correct commit timestamps, while reinserts and previous removes preserve MVCC gaps.

Dependencies/integration points: tests role transition, ingest drain, stable reconciliation, timestamp reads, and layered tombstone semantics. Risks are timestamp ordering regressions and boundary ownership bugs between stable windows and ingest entries. Test signals are exhaustive key sweeps plus timestamped point reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate16.py -->
