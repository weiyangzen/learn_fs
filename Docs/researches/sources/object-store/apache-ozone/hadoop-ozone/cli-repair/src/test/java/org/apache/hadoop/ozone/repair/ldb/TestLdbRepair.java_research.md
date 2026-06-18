## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/ldb/TestLdbRepair.java

Purpose: functional test for manual RocksDB column-family compaction.

Important APIs and control flow: setup creates a real temp `RDBStore` with a test column family and enables codec leak detection. The test inserts many keys, flushes, records SST size, deletes keys to create tombstones, flushes, closes the store, snapshots representative DB/table options, executes `RocksDBManualCompaction` with confirmation input, and then verifies SST size decreased, live SST metadata reports zero deletions, and RocksDB options are unchanged.

State and dependencies: mutates a real temp RocksDB directory. Uses `DBStoreBuilder`, `RocksDBUtils`, `RdbUtil`, managed RocksDB wrappers, and option inspection wrappers.

Risks and test signals: provides high-value evidence that compaction has the intended storage effect without changing RocksDB options. It does not test missing column-family or declined-confirmation paths.
