# sources/storage-engines/wiredtiger/test/suite/test_drop01.py

Purpose: intended to test that dropping a table removes associated history-store records, but the test is currently skipped for known WT-16857.

Important APIs and control flow: helpers commit timestamped updates to a two-column-group table and count entries by opening `file:WiredTigerHS.wt`. The skipped test creates column groups, writes two timestamped versions of one key, checkpoints, expects two history-store records, drops the table, and expects history-store size zero.

State and persistence: covers timestamped updates, checkpoint-created history-store records, and drop cleanup across column groups.

Dependencies and integration: uses `wttest`, `unittest.skip`, timestamp commit strings, history store file cursor, table/colgroup metadata.

Risks and test signals: because it is skipped, it documents a desired invariant rather than enforcing it. If enabled, failures would indicate incomplete history-store truncation on drop.
