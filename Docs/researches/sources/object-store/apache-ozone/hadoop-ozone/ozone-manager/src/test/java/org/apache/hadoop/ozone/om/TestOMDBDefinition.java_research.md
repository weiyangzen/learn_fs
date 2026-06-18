# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMDBDefinition.java

Purpose: Consistency test ensuring `OMDBDefinition` column-family definitions match the tables actually opened by `OmMetadataManagerImpl`.

Important APIs and types: `OMDBDefinition.get`, `DBColumnFamilyDefinition`, `OmMetadataManagerImpl.loadDB`, `DBStore.getTableNames`, `OmReadOnlyLock`, and `OzoneConfiguration`.

Control flow: the test collects defined column-family names from `OMDBDefinition`, opens a temporary OM DB store via metadata manager loading, removes RocksDB's default table, subtracts names in both directions, and asserts no missing entries plus equal counts.

State and persistence: creates a temporary RocksDB-backed OM DB and closes it with try-with-resources. The test validates schema metadata, not data rows.

Dependencies and integration points: guards the codec/definition layer used by tooling, checkpoint inspection, and metadata manager table initialization. It catches table additions that update only one side of the schema contract.

Risks and edge cases: the error messages appear label-swapped in spirit but still expose missing names. The test can fail on intentional table additions until both definitions and manager loading are synchronized.

Test signals: zero missing definition tables, zero missing OM DB tables, and equal counts between loaded RocksDB column families and `OMDBDefinition`.
