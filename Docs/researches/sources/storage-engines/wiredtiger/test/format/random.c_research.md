# sources/storage-engines/wiredtiger/test/format/random.c

Purpose: optional background smoke test for random cursors on row-store tables.

Important APIs and functions: `random_kv`, `table_select_type`, `wt_wrap_open_session`, `wt_wrap_open_cursor`, random cursor config `next_random=true` and `next_random_sample_size=37`, cursor `next/get_key/get_value/close`.

Control flow: exits if no row-store table exists. It opens a session, alternates between simple and sample-size random cursor configurations, selects a row-store table, performs up to 1,000 `next` calls, tolerates normal transient returns, reads returned key/value pairs, closes the cursor, sleeps 1 to 10 seconds, and repeats until `g.workers_finished`.

State and persistence: read-only except transient cursor/session state and cache effects. It samples live data while concurrent writes continue.

Dependencies and integration: spawned by `operations` under `GV(OPS_RANDOM_CURSOR)`. It depends on row-store table metadata, global extra RNG, and session prefetch wrapper behavior.

Risks and test signals: it intentionally does not validate key distribution, only API stability. Unexpected cursor errors are the main failure signal. It is skipped for pure column-store workloads.
