# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDataValidate.java

Purpose: Abstract base integration test for Freon `RandomKeyGenerator` write-validation behavior on a five-datanode Ratis cluster.

Important APIs, types, and functions: Provides static `startCluster` and `shutdownCluster`, and tests `ratisTestLargeKey` and `validateWriteTest`. Uses `MiniOzoneCluster`, `DatanodeRatisServerConfig`, `RatisClientConfig.RaftConfig`, `OZONE_SCM_RATIS_PIPELINE_LIMIT`, `RandomKeyGenerator`, and picocli `CommandLine`.

Control flow: `startCluster` shortens Ratis request/watch timeouts, sets pipeline limit to eight, starts five datanodes, waits for readiness, and waits for a Ratis THREE pipeline. `ratisTestLargeKey` writes one 20 MB key with `--validate-writes` and asserts one volume, one bucket, one key, and zero validation failures. `validateWriteTest` writes 2 volumes * 5 buckets * 10 keys with Ratis THREE validation and asserts expected creation counts, validation enabled, non-zero validated/success counts, and zero unsuccessful validations.

State and persistence behavior: Tests create real volumes, buckets, keys, and replicated Ratis containers. `RandomKeyGenerator` stores counters for created volumes/buckets/keys and validation outcomes. Cluster state is static and shared by concrete subclasses.

Dependencies and integration points: Integrates Freon CLI, Ozone object store writes, Ratis replication, client/datanode timeouts, and read-back validation of generated data.

Risks: Large-key and multi-key tests can be slow. Static cluster lifecycle is controlled by subclasses, so missing shutdown would leak resources. Counter assertions depend on `RandomKeyGenerator` semantics.

Test signals: Exact creation counts, `getValidateWrites` true, positive validation counts, and zero unsuccessful validation count.
