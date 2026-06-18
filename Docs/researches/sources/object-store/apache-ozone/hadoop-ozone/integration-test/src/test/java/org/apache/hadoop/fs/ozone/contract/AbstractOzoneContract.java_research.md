# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/AbstractOzoneContract.java

Purpose: base Hadoop filesystem contract wrapper for Ozone-backed tests.

Important APIs/types/functions: extends `AbstractFSContract`, stores a `MiniOzoneCluster`, declares abstract `getRootURI`, exposes `getCluster`, and implements `getTestFileSystem` by setting `fs.defaultFS` to the concrete Ozone root URI and returning `FileSystem.get(getConf())`.

Control flow: concrete contract supplies the URI; this base validates the cluster exists, mutates the contract configuration, and opens the filesystem.

State and persistence behavior: no Ozone metadata is created here directly. It controls client configuration state used by downstream contract tests.

Dependencies and integration points: integrates Hadoop contract test framework with `MiniOzoneCluster` and Ozone concrete contract classes such as `OzoneContract` and rooted variants.

Risks: `fs.defaultFS` is mutated on the shared contract configuration, so concrete tests must supply an isolated or stable configuration. If `getRootURI` creates buckets, that side effect is owned by the subclass.

Test signals: failures here usually mean cluster setup or URI construction is broken before contract tests can run.
