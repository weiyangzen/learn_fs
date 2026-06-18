# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestCompactionService.java

Purpose: Unit-tests `CompactionService` table selection and periodic execution without running real RocksDB compaction. Important APIs and types include `CompactionService`, mocked `OzoneManager`, `OMMetadataManager`, `TypedTable`, compaction config keys, `GenericTestUtils.waitFor`, and `ExitUtils`.

Control flow: `setup` enables compaction, configures a tiny interval, mocks OM metadata table lookup/listing, and exposes a set of valid table names. Tests create an anonymous `CompactionService` overriding `compactFully` to log only. Success starts/suspends/resumes the service and waits for `getNumCompactions`. Invalid-table coverage confirms mixed valid/invalid config keeps valid tables and all-invalid config throws.

State and persistence behavior: The service maintains in-memory counters, table-name filtering, and background scheduling state. No real table data is compacted. Dependencies and integration points are OM table registry, service lifecycle methods, configured column-family lists, and periodical task scheduling.

Risks: Timing uses millisecond intervals and short sleeps; failures can be scheduler-sensitive. Test signals are compaction count growth, compactable table membership, invalid table exclusion, and constructor exception for no valid tables.
