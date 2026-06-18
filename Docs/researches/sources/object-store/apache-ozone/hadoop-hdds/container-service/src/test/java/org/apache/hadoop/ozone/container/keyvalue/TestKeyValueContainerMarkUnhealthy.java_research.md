# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainerMarkUnhealthy.java

Purpose: tests `KeyValueContainer.markContainerUnhealthy()` state transitions and persistence for every container layout version.

Important APIs/types/functions: `KeyValueContainer.markContainerUnhealthy`, `markContainerForClose`, `close`, `quasiClose`, `ContainerDataYaml.readContainerFile`, `HddsVolume.format/createWorkingDir`, mocked `MutableVolumeSet`, and `ContainerLayoutTestInfo.ContainerTest`.

Control flow: `initTestData()` selects a layout and calls `setup()`, which creates an HDDS volume under `@TempDir`, mocks volume choosing to return it, builds `KeyValueContainerData`, assigns a metadata path, and constructs a `KeyValueContainer`. Tests mark open, closed, quasi-closed, and closing containers unhealthy, and assert closing an already unhealthy container throws `StorageContainerException`.

State and persistence behavior: marking unhealthy updates in-memory `KeyValueContainerData` state and, for created containers, the `.container` file. Closed/quasi-closed tests create the container first to avoid close/quasi-close sync/compaction null paths. The open-container test reads the container YAML back to verify persisted `UNHEALTHY`.

Dependencies and integration points: integrates state-machine transitions with volume setup and container YAML persistence. Uses AssertJ and JUnit exception assertions.

Risks and test signals: focused signal for unhealthy transition permissiveness and close rejection. It does not test handler-level ICR/report side effects; those are covered elsewhere.
