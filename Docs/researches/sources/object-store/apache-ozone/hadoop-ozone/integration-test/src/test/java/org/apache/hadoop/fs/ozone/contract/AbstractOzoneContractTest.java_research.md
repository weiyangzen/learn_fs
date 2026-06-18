# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/AbstractOzoneContractTest.java

Purpose: shared JUnit 5 host for Hadoop filesystem contract tests against a single `MiniOzoneCluster`, using nested classes to run create, delete, status, mkdir, open, rename, root, seek, unbuffer, distcp, and lease-recovery contracts.

Important APIs/types/functions: `createOzoneContract(Configuration)` is implemented by subclasses. `createOzoneConfig` builds base Ozone config and adds `contract/ozone.xml`; `createCluster` starts a five-DN mini cluster. Nested classes override `createConfiguration` and `createContract` for each Hadoop contract suite. OFS root-directory tests use AssertJ assumptions to skip cases unsupported by rooted OFS. Lease recovery contract tests run only when default bucket layout is FSO.

Control flow: `ClusterForTests` manages cluster lifecycle. Each nested contract class creates a fresh configuration but points to the same cluster-backed Ozone contract. The DistCp nested class additionally cleans local test directories in teardown.

State and persistence behavior: nested tests create and mutate filesystem state according to Hadoop contract expectations. Root-directory tests avoid unsupported recursive volume/root deletion paths for OFS. Lease recovery is gated to FSO because only that layout supports the tested recovery semantics.

Dependencies and integration points: depends on Hadoop contract test classes, `AbstractContractDistCpTest`, `ClusterForTests`, Ozone bucket layout config, OFS URI scheme, and `contract/ozone.xml` behavior declarations.

Risks: contract tests are broad and may exercise unsupported Hadoop assumptions; skip assumptions document known OFS differences. Shared cluster speeds execution but can make poor cleanup visible across nested suites.

Test signals: provides broad compatibility coverage for Hadoop `FileSystem` contract behavior and pinpoints where Ozone intentionally diverges for OFS root operations or non-FSO lease recovery.
