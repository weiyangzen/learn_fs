# sources/storage-engines/wiredtiger/test/suite/test_checkpoint25.py

Purpose: timestamped counterpart to fast-delete checkpoint reading. It verifies that checkpoint cursors handle fast-deleted pages correctly across historical, default, and no-read-timestamp reads after optional timestamp advancement and reopen.

Important APIs and types: timestamped `session.truncate`, `stat.conn.rec_page_delete_fast`, checkpoint cursor `debug=(checkpoint_read_timestamp=...)`, `set_timestamp`, and `make_scenarios` over oldest/stable advancement.

Control flow: write data at timestamp 10, make it stable and reopen, fast-truncate the middle half at timestamp 20, set stable 20, verify fast-delete stats, checkpoint, optionally advance oldest/stable and reopen, then read the checkpoint at timestamps 15, 25, default, and 0.

State and persistence behavior: the checkpoint must preserve both pre-truncate and post-truncate views. Historical reads at 15 see all rows; newer/default/no-read-timestamp views see only surviving rows.

Dependencies and integration points: covers row/column stores, named/unnamed checkpoints, timestamp advancement, history-store visibility, and fast-delete reconciliation. Skipped for tiered/disaggregated hooks.

Risks: broad scenario matrix can be expensive. The zero-count argument is not directly checked against cursor holes for column-store beyond count/value assertions.

Test signals: fast-delete statistic is positive; read timestamp 15 returns all rows; read timestamp 25/default/0 return half the rows.
