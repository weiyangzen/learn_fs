# sources/storage-engines/wiredtiger/test/suite/test_checkpoint26.py

Purpose: validates the `timing_stress_for_test=[checkpoint_evict_page]` mode, which makes checkpoint evict reconciled pages, and confirms checkpoint-driven eviction is observable in statistics.

Important APIs and types: `WiredTigerTestCase`, `stat.conn.eviction_pages_in_parallel_with_checkpoint`, `session.checkpoint`, and `make_scenarios` for precise versus fuzzy checkpoint.

Control flow: create a table with integer keys and large string values, insert 10,000 records in separate transactions, assert the checkpoint-eviction statistic is initially zero, run checkpoint, and assert the statistic is now positive.

State and persistence behavior: the table is large enough to produce dirty pages but uses a large cache and high dirty targets so ordinary eviction should not run before checkpoint. Persistence is validated indirectly by checkpoint eviction statistics.

Dependencies and integration points: uses WiredTiger connection configuration for cache, dirty eviction targets, all statistics, and timing stress. Precise checkpoint mode needs a stable timestamp set first.

Risks: statistic isolation is important; unexpected eviction before checkpoint would invalidate the initial assertion. The test does not scan data after checkpoint.

Test signals: zero `eviction_pages_in_parallel_with_checkpoint` before checkpoint, greater than zero after checkpoint.
