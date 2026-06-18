# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestContainerLayoutVersion.java

Purpose: This compact test locks down the public enum-like contract of `ContainerLayoutVersion`. It verifies the currently supported layout count and the numeric IDs used by file-per-chunk and file-per-block layouts.

Important APIs and types: It imports `ContainerLayoutVersion`, `FILE_PER_CHUNK`, and `FILE_PER_BLOCK`. The tests call `ContainerLayoutVersion.getAllVersions()`, `getVersion()` on each constant, and JUnit `assertEquals`.

Control flow: The suite has three independent tests: `testVersionCount` asserts two known layout versions, `testV1` asserts `FILE_PER_CHUNK` has version 1, and `testV2` asserts `FILE_PER_BLOCK` has version 2.

State and persistence behavior: There is no filesystem or DB persistence. The only state is static layout metadata compiled into `ContainerLayoutVersion`.

Dependencies and integration points: These constants are used by chunk managers, container persistence, deletion service tests, YAML persistence, and parameterized layout tests elsewhere in this subset. This file provides a fast compatibility guard for serialization and upgrade-sensitive numeric layout IDs.

Risks: The version-count assertion must be updated deliberately if a new layout is added. A new layout addition would fail this test even if backward compatibility is preserved, which is useful as a prompt to update broader tests.

Test signals: Exact numeric equality for version count and per-layout IDs.
