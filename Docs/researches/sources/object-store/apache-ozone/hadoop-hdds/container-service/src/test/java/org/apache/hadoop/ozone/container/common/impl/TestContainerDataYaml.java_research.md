# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestContainerDataYaml.java

Purpose: This suite verifies `.container` YAML creation and reading for `KeyValueContainerData`, backward-compatible parsing of files with additional fields, checksum verification, optional replica-index persistence, and exclusion of data checksum from the container file.

Important APIs and types: It uses `ContainerDataYaml.createContainerFile`, `readContainerFile`, `getYamlForContainerType`, `ContainerUtils.verifyContainerFileChecksum`, `KeyValueContainerData`, `ContainerLayoutTestInfo.ContainerTest`, `VersionedDatanodeFeatures.SchemaV2`, `ContainerLayoutVersion`, and resource files `incorrect.container`, `additionalfields.container`, and `incorrect.checksum.container`.

Control flow: `createContainerFile` builds a key-value container data object, sets DB type, paths, scan time, schema v2, replica index, and a data checksum, then writes YAML. `testCreateContainerFile` reads it back, checks all fields, updates metadata and state, rewrites, and rechecks. Other tests verify zero replica index is omitted from YAML, malformed enum data throws, additional unknown fields remain readable, container-file checksum validates, data checksum is not persisted in `.container`, checksum with replica index validates, incorrect checksum is detected, and checksum verification can be disabled by config.

State and persistence behavior: The persistent artifact is the `.container` YAML file. The tests distinguish container-file checksum from data checksum: file checksum is persisted and verified, while container data checksum lives elsewhere and should read as zero from YAML. Scan timestamps, state, metadata, paths, layout, schema, and replica index are persisted as appropriate.

Dependencies and integration points: This is central to container load, upgrade, rollback, checksum validation, and YAML compatibility. It integrates config-controlled checksum verification and layout-parameterized serialization.

Risks: Resource files encode compatibility expectations and must be maintained when YAML schema changes. Exact omission of `replicaIndex` when zero is a wire-format contract. The test recalculates paths in temp directories, so checksum behavior must account for path-sensitive fields.

Test signals: Field round trips, metadata update persistence, absence of `replicaIndex` for zero, `No enum constant` on bad enum, successful read of additional fields, checksum validation success/failure, disabled-checksum pass, and data checksum reading as zero from the container file.
