# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestKeyValueContainerData.java

Purpose: This suite verifies `KeyValueContainerData` defaults, mutators, statistics, copy-constructor behavior, schema selection, replica index, pending-delete accounting, and data checksum state.

Important APIs and types: It uses `ContainerTestVersionInfo.ContainerTest`, `KeyValueContainerData`, `ContainerData.Statistics`, `ContainerLayoutVersion`, `ContainerProtos.ContainerDataProto.State`, mocked `HddsVolume`, `VersionedDatanodeFeatures.SchemaV3.chooseSchemaVersion`, and `StorageUnit.GB`.

Control flow: `initVersionInfo` sets the parameterized layout and schema into a fresh `OzoneConfiguration`. `testKeyValueData` constructs a container data object, verifies defaults, mutates state and paths, updates read/write/block stats, increments pending deletes, sets schema version and data checksum, then verifies the copy constructor resets volatile deletion counters while preserving replica index and schema. `testNeedsDataChecksum` checks the distinction between missing checksum and an explicitly set checksum value, including zero.

State and persistence behavior: There is no on-disk persistence in this test. It verifies in-memory metadata, statistics counters, pending-delete counters, delete transaction ID, replica index, origin IDs, schema version, and checksum sentinel behavior. The checksum test is important because `0` can mean either "not generated yet" or "generated hash is zero" depending on whether the setter has been called.

Dependencies and integration points: The class is a core data carrier for YAML persistence, block deletion metadata, container reports, schema-aware DB access, and checksum tree management. Parameterized execution gives coverage for all container layout/schema combinations exposed by `ContainerTestVersionInfo`.

Risks: The copy-constructor behavior intentionally does not preserve pending deletion counters and transaction ID; downstream code relying on copied objects must account for that. The test uses a mocked volume, so committed-space side effects are covered elsewhere.

Test signals: Exact defaults, statistic assertions, pending-delete counters, schema and checksum values, copy-constructor reset of pending deletion state, `needsDataChecksum` transitions, and negative checksum rejection.
