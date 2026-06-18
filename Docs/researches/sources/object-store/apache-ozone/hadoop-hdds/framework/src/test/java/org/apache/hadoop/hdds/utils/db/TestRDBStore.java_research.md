# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBStore.java

Purpose: Unit and integration tests for `RDBStore`, the RocksDB-backed database store abstraction used by HDDS/Ozone metadata components.

Important APIs/types/functions: `newManagedDBOptions`, `newRDBStore`, `RDBStore.getTable`, `listTables`, `flushDB`, `compactDB`, `compactTable`, `getCheckpoint`, `getUpdatesSince`, `getEstimatedKeyCount`, `RDBTable`, `DBCheckpoint`, `DBUpdatesWrapper`, and `TableConfig`.

Control flow: Setup builds a temporary RocksDB with default plus named column families and statistics enabled. Tests write random rows, flush and compact DB/table data, inspect table listing and missing-table errors, create checkpoints, reopen from checkpoints, request update batches by sequence number, simulate reopening with a removed configured family, and compare SST files between checkpoints.

State and persistence behavior: The tests exercise RocksDB column-family state, live file metadata, checkpoint directories, sequence numbers, WAL/update wrappers, persisted rows across reopen, and cleanup of checkpoint directories.

Dependencies and integration points: Depends on RocksDB `Statistics`, managed RocksDB option wrappers, Ozone constants for SST suffixes, temporary files, and byte-array tables.

Risks: Some estimates are checked with loose bounds and the assertions use `||` where an intended range may have been `&&`, reducing precision. `compareSstWithSameName` reads file lists from `checkpoint1` twice, so same-name comparison may miss files present only in the second checkpoint. Random data makes exact debugging harder.

Test signals: Covers store lifecycle, compaction, checkpoint generation/cleanup, update extraction limits, downgrade column-family behavior, table lookup/listing, and leak detection through `CodecBuffer`.
