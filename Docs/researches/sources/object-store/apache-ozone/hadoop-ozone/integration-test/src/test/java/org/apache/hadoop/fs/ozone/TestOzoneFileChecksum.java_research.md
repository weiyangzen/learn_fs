# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileChecksum.java

Purpose: verifies Ozone `FileSystem.getFileChecksum` produces the same checksum for EC and replicated data across many sizes, checksum granularities, topology-aware read modes, and missing datanodes.

Important APIs/types/functions: setup creates a five-DN cluster with 1 MiB chunks and 2 MiB blocks. `testEcFileChecksum` parameterizes missing datanode indexes and `ozone.client.bytes.per.checksum`, creates a legacy replicated bucket and an EC bucket, writes identical data via `BasicRootedOzoneClientAdapterImpl.createFile`, records replicated checksums, shuts down selected datanodes, then compares EC checksums under topology-aware true and false. `missingIndexesAndChecksumSize` supplies six failure/checksum-size combinations.

Control flow: for each data size in two generated arrays, write replicated data, compute checksum, write EC data, then after DN shutdowns open a fresh filesystem for each topology mode and compare EC checksum hex to the recorded replicated checksum.

State and persistence behavior: persists two copies of each random object, one replicated and one EC. Datanode shutdown simulates missing EC fragments while checksum reconstruction should remain deterministic and equal to replicated checksum semantics.

Dependencies and integration points: uses `MiniOzoneCluster`, `RootedOzoneFileSystem`, `BasicRootedOzoneClientAdapterImpl`, `FileChecksum`, EC replication config `RS-3-2-1024k`, network topology aware read config, and Hadoop checksum byte formatting.

Risks: many large data sizes make this an expensive test. Random data and datanode shutdowns can amplify flaky reconstruction or timeout behavior. It assumes two missing indexes remain within EC tolerance.

Test signals: detects checksum algorithm drift, EC reconstruction checksum mismatches, topology-aware read regressions, and failure to serve checksums when tolerated datanodes are unavailable.
