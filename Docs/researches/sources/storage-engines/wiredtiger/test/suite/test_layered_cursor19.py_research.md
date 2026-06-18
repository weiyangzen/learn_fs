# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor19.py

Purpose: validates follower write cursor open behavior for layered cursors. With overwrite enabled, follower insert/update should write to ingest without opening stable; with `overwrite=false`, the operation must check for existing stable data and therefore open the stable constituent.

Important APIs and functions: `test_layered_cursor19` uses `DisaggConfigMixin`, `@disagg_test_class`, statistics cursor access via `stat.conn.cursor_create_count`, helper methods `get_conn_stat`, `measure_cursor_opens`, and `seed_leader_and_advance_follower`, plus cursor configurations `overwrite=true` and `overwrite=false`.

Control flow: setup creates the layered table and a follower connection. `seed_leader_and_advance_follower` writes stable rows on the leader, checkpoints, and advances the follower. Each test measures the delta in connection cursor-create count around one follower insert or update. Overwrite tests assert only ingest-open overhead; no-overwrite tests assert additional stable cursor opens.

State and persistence behavior: stable rows are checkpointed leader state, while follower writes land in ingest. The test observes implementation behavior indirectly through cursor creation statistics rather than data reads, making it sensitive to constituent-open decisions in the write path.

Dependencies and integration: integrates with WiredTiger statistics, disaggregated leader/follower setup, layered overwrite semantics, and cursor open accounting. Risks include performance regressions from unnecessary stable opens, correctness regressions when no-overwrite skips stable existence checks, and stat noise from unrelated cursor activity. Test signals compare measured cursor-create deltas against expected thresholds for overwrite and no-overwrite cases.
