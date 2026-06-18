# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor20.py

Purpose: follower cached-cursor coverage for standby-style cursor opening. It checks that repeated follower cursor opens over layered URIs reuse cached constituent cursors enough to stay below a cursor-create limit.

Important APIs and functions: `test_layered_cursor20` uses `@disagg_test_class`, leader and follower disaggregated configurations, `stat.conn.cursor_create_count`, helper methods `show_cursor_create_stats` and `check_cursor_create_stats`, and `disagg_advance_checkpoint`. The main test is `test_standby_open_cursor`.

Control flow: the leader creates multiple layered tables, writes data with timestamped transactions, checkpoints, and advances the follower. The follower repeatedly opens and closes cursors over the layered URIs while the test samples cursor-create statistics before and after the operation batch.

State and persistence behavior: stable checkpoint metadata is shared from leader to follower. The state under test is not row content but internal cursor cache behavior on the follower, especially whether layered cursors repeatedly create stable/ingest constituent cursors.

Dependencies and integration: depends on WiredTiger connection statistics, disaggregated checkpoint advance, layered cursor opening, and the test harness follower connection. Risks include cache leaks, excessive cursor creation, failure to cache stable constituent cursors, or stale cached cursor state if reused unsafely. Test signals are statistic thresholds in `check_cursor_create_stats`, supplemented by diagnostic stat printing.
