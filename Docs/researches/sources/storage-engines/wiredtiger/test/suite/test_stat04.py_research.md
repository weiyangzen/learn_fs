<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat04.py

Purpose: validates that the `btree_entries` statistic accurately tracks key/value pair counts through inserts, removes, and reopen for row and column stores with different value sizes.

Important APIs/types/functions: `test_stat04` uses `suite_subprocess`, `make_scenarios`, `stat.dsrc.btree_entries`, and helpers `init_test`, `genkey`, `genvalue`, and `checkcount`. Scenarios cover small, medium, large, and jumbo value workloads.

Control flow: create a table for the selected key format and workload size, insert entries while checking count every 50 records, remove a deterministic subset by modular key selection and check after each successful remove, close the cursor, reopen the connection, and verify the final count again.

State and persistence behavior: the statistic must be correct both in memory and after the btree is written and reopened. Jumbo values also exercise overflow/value storage while preserving entry counts.

Dependencies/integration points: covers row/column key generation, statistics with `clear`, large data volumes, and persistent btree metadata. Risks include runtime for large scenarios and exact count tracking under duplicate removal attempts; signals are exact `btree_entries` equality throughout.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat04.py -->
