<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/MiniOzoneLoadGenerator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/MiniOzoneLoadGenerator.java

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/MiniOzoneLoadGenerator.java_research.md`.

## Purpose
Factory and lifecycle wrapper for chaos-test load generators, creating Ozone buckets with requested layouts and replication settings and running them through `LoadExecutors`. The file has 148 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Types/classes: `MiniOzoneLoadGenerator, Builder`. Methods and hooks: `MiniOzoneLoadGenerator, addLoads, startIO, shutdownLoadGenerator, addLoadGenerator, setOMServiceId, setConf, setNumBuffers, setNumThreads, setVolume, setBucketArgs, build`. Test annotations present: `0`.

## Control Flow
The file runs through test/framework lifecycle methods or direct method calls shown above; assertions and helper calls drive observable behavior.

## State And Persistence Behavior
No production persistence; tests mutate local fixtures and assert in-memory responses or utility structures.

## Dependencies And Integration Points
imports `java.util.ArrayList`, `java.util.HashSet`, `java.util.List`, `java.util.Set`, `java.util.concurrent.TimeUnit`, `org.apache.commons.lang3.RandomStringUtils`, `org.apache.hadoop.hdds.conf.OzoneConfiguration`, `org.apache.hadoop.ozone.client.BucketArgs`.

## Risks And Edge Cases
- Assertions focus on visible behavior in this file; regressions outside the covered cases may need broader tests.
- Shared static fixtures can make test order and mutation restoration important.

## Test Signals
Signals come from chaos-test completion, propagated future exceptions, JUnit assertions in `LoadBucket`, mini-cluster readiness waits, and generated test reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/MiniOzoneLoadGenerator.java -->
