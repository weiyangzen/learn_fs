# sources/storage-engines/wiredtiger/test/suite/test_cursor_random03.py

Purpose: regression test for WT-12225, where two random cursors opened close together could produce identical streams because the random seed pattern repeated.

Important APIs and control flow: creates `table:random` with exactly 2135 rows and `leaf_page_max=100MB`, then loops 5000 times. Each loop records 100 keys from a first `next_random=true` cursor, closes it, opens a second random cursor, and checks that at least one of the next 100 keys differs at the same position.

State and persistence: state is transient table content plus in-memory `random_keys`. There is no checkpoint or restart; the timing-sensitive risk is exercised by opening cursors back to back.

Dependencies and integration: uses `wttest` and `SimpleDataSet`. The fixed record count is part of the bug reproducer because it shapes random skip-list estimation.

Risks and test signals: a false failure is possible only if two independent random streams happen to match for 100 positions, which is extremely unlikely. Failure points at cursor random seeding or `__wt_random` behavior.
