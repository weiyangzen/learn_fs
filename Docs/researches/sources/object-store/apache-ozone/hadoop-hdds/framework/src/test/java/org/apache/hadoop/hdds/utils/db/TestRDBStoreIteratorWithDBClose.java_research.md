# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBStoreIteratorWithDBClose.java

Purpose: Regression tests for safe iterator behavior while `RDBStore`/RocksDB is closed concurrently.

Important APIs/types/functions: `RDBStore.close`, `RDBTable.iterator`, `Table.KeyValueIterator`, `IteratorType.KEY_AND_VALUE`, `hasNext`, `forEachRemaining`, iterator `close`, and package-private `RDBTable.isClosed`.

Control flow: Setup creates a temporary store, table, and 100 entries. Tests launch scanner threads, close the DB mid-iteration, verify `hasNext` returns false without exceptions, prove physical DB close waits for open iterator references, validate end-to-end concurrent close/scan races, test `forEachRemaining` under close, and ensure iterator close after DB close does not throw.

State and persistence behavior: Real RocksDB data is written before concurrency tests. Main state under test is the DB closed flag and internal reference counter preventing physical close while iterators are open.

Dependencies and integration points: Uses Java executors, futures, latches, atomics, temporary RocksDB stores, and shared helpers from `TestRDBStore`.

Risks: Timing-based sleeps can be flaky on slow or overloaded hosts. Tests intentionally block close until iterator release, so leaked iterators would hang. Shutdown of executors is manual.

Test signals: High-value concurrency signal for volume-failure/background-scanner races and native crash prevention when RocksDB is closed during scans.
