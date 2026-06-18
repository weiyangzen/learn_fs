# sources/storage-engines/wiredtiger/test/suite/test_empty_value.py

Purpose: smoke tests row-store zero-length values and verifies they are represented as empty values rather than stored payloads.

Important APIs and control flow: creates `file:test_empty_values` with `key_format=S,value_format=u`, inserts 25000 records with `b''`, reopens the connection to force disk readback, opens `statistics:<uri>` with `statistics=(tree_walk)`, and reads `stat.dsrc.btree_row_empty_values`.

State and persistence: zero-length values are persisted through reopen. Tree-walk statistics count optimized empty-value cells.

Dependencies and integration: uses `wiredtiger.stat`, `wttest`, file btree storage, and tree-walk statistics.

Risks and test signals: the statistic must equal the number of inserted records. Failure indicates empty values were stored incorrectly or not counted during tree walk.
