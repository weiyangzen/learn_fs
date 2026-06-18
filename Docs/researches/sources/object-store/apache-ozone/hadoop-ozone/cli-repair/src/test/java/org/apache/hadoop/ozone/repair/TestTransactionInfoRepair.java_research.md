## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/TestTransactionInfoRepair.java

Purpose: parameterized tests for shared OM/SCM transaction-info repair behavior through the `OzoneRepair` command tree.

Important APIs and control flow: for both `om` and `scm`, static mocks replace `ManagedRocksDB.openWithLatestOptions`, `RocksDBUtils.getColumnFamilyHandle`, and `RocksDBUtils.getValue`. The test executes `<component> update-transaction --db testDBPath --term 1 --index 1` after confirming stdin. It verifies successful output, missing column-family errors, and RocksDB put failure handling.

State and dependencies: no real DB is written; mocked `ManagedRocksDB` and `RocksDB` simulate persistence. It depends on OM and SCM DB definitions for the expected transaction-info table names.

Risks and test signals: covers CLI wiring and error messages but not real RocksDB serialization side effects. It is a useful regression test for component-specific table selection.
