<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/states/TestContainerAttribute.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/states/TestContainerAttribute.java

Purpose: This suite tests `ContainerAttribute`, the generic index structure that maps enum attributes to ordered `ContainerID -> ContainerInfo` collections.

Important APIs and types: It uses `ContainerAttribute<Key>`, `ContainerID`, `ContainerInfo`, `SCMException`, `NavigableMap`, and an internal enum `Key { K1, K2, K3 }`. Helpers `hasContainerID` inspect a key bucket directly.

Control flow: `testAddNonExisting` adds one container and verifies duplicate add throws `IllegalStateException`. `testClearSet` fills all enum buckets with 100 containers and clears one bucket. `testRemove` removes odd IDs from one bucket while confirming other buckets are untouched. `tesUpdate` moves an ID between buckets and verifies updating from a bucket that does not contain the ID throws `SCMException`.

State and persistence behavior: State is entirely in-memory ordered maps per enum key. No DB or filesystem is involved.

Dependencies and integration points: `ContainerAttribute` underpins SCM container state indexing and fast lookup by lifecycle or other enum dimensions. The test guards bucket isolation, duplicate protection, and atomic move semantics.

Risks: A regression in add/remove/update can corrupt state indexes even if the canonical container table is correct. The test does not cover concurrency.

Test signals: Assertions cover collection sizes, map membership, duplicate-add failure, clear behavior, odd-ID removal, successful movement across buckets, and missing-source update failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/states/TestContainerAttribute.java -->
