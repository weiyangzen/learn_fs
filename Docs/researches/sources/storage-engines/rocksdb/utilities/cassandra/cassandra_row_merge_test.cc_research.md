## `sources/storage-engines/rocksdb/utilities/cassandra/cassandra_row_merge_test.cc`

Purpose: focused unit tests for `RowValue::Merge()`. It validates column-level timestamp conflict resolution and row tombstone handling independent of a live RocksDB instance.

Important test cases: `RowValueMergeTest.Merge` merges three row values containing normal columns, expiring columns, and tombstones at overlapping indexes, expecting the highest-timestamp mutation per column and preserving distinct indexes. `RowValueMergeTest.MergeWithRowTombstone` checks that a row tombstone suppresses older columns, allows newer columns, and wins entirely when the latest mutation is a row tombstone.

Control flow: tests build `std::vector<RowValue>` with helper-created rows, call `RowValue::Merge(std::move(row_values))`, and verify the resulting row shape and ordered columns with `VerifyRowValueColumns()`. The second test reuses the vector after move by adding new tombstone values and checking latest tombstone behavior.

State and persistence behavior: no DB persistence occurs. The tests define semantic merge output for serialized row values that the merge operator later depends on.

Dependencies and integration: uses RocksDB test harness, Cassandra `format.h`, and `test_utils.h`. It has its own GoogleTest `main()`.

Risks: coverage is compact and deterministic but does not test malformed rows, duplicate equal timestamps, or very large operand lists. The vector reuse after move is valid because the moved-from vector is reused by pushing new values, but it is a pattern worth reading carefully.

Test signals: this is the direct regression signal for row merge semantics used by Cassandra merge operator and functional DB tests.
