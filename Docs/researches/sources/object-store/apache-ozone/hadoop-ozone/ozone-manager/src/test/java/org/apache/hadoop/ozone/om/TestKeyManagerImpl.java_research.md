<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestKeyManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestKeyManagerImpl.java

Purpose: Parameterized unit tests for `KeyManagerImpl` table-scanning helpers used to fetch deleted keys, renamed keys, and deleted directories.

Important APIs/types/functions: `getTableIteratorParameters` defines combinations of volume/bucket filters, start offsets, result limits, and expected exceptions. `mockTableIterator` builds sorted synthetic table keys and configures `Table.iterator(startKey)` with `MapBackedTableIterator`. Tests call `getDeletedKeyEntries`, `getRenamesKeyEntries`, and `getDeletedDirEntries` on a `KeyManagerImpl` with mocked metadata manager tables.

Control flow: Each parameterized test builds a table with deterministic `/volumeNN/bucketNN/keyNN` style keys, applies optional volume/bucket/start filters and a predicate, computes expected limited results, then compares the helper result or expects an exception for invalid volume/bucket filter combinations.

State and persistence behavior: No real persistence. Uses in-memory `TreeMap` and mocked OM DB tables to simulate ordered RocksDB iteration.

Dependencies and integration points: Protects key-manager scanning over `DELETED_TABLE`, `SNAPSHOT_RENAMED_TABLE`, and `DELETED_DIR_TABLE`, plus metadata manager bucket-prefix calculation. These helpers feed deletion/snapshot maintenance workflows.

Risks: The expected data generation mirrors implementation assumptions about key formatting, so shared mistakes in prefix format could pass. It covers iterator order and limits but not real RocksDB iterator resource handling. Deleted-dir tests force `startVolumeNumber` null, so start-key pagination for that path is narrower.

Test signals: Passing confirms filtered table scans honor volume/bucket constraints, start offsets, predicates, limits, value conversion for repeated deleted keys, and invalid filter validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestKeyManagerImpl.java -->
