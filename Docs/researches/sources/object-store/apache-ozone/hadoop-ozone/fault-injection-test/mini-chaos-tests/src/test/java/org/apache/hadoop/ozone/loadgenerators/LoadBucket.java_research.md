<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/loadgenerators/LoadBucket.java -->
# sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/loadgenerators/LoadBucket.java

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/loadgenerators/LoadBucket.java_research.md`.

## Purpose
Shared chaos-test adapter around `OzoneBucket` and `OzoneFileSystem` that performs write, read, delete, and directory operations through either object-store or filesystem APIs. The file has 320 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Types/classes: `LoadBucket, Op, DirectoryOp, WriteOp, ReadOp, DeleteOp`. Methods and hooks: `LoadBucket, isFsOp, writeKey, writeKey, createDirectory, readDirectory, readKey, readKey, deleteKey, deleteKey, getFSUri, getFSUri, Op, execute, doFsOp, DirectoryOp`. Test annotations present: `0`.

## Control Flow
Public write/read/delete/directory methods create an `Op` subclass; `Op.execute()` chooses filesystem or object-store path, runs the concrete operation, executes post-operation validation/cleanup, logs failures, and rethrows errors.

## State And Persistence Behavior
State is mostly test-runtime state: mini-cluster processes, failed-node sets, scheduled futures, executor futures, random key indexes, Ozone buckets/keys/directories, and generated data buffers. Persistence is through Ozone object-store/filesystem writes during the test run.

## Dependencies And Integration Points
imports `static org.junit.jupiter.api.Assertions.assertEquals`, `static org.junit.jupiter.api.Assertions.assertTrue`, `java.io.IOException`, `java.io.InputStream`, `java.io.OutputStream`, `java.net.URI`, `java.net.URISyntaxException`, `java.nio.ByteBuffer`.

## Risks And Edge Cases
- Randomized failure and IO ordering can expose flaky timing, quorum, and readiness assumptions.
- Tests are resource-heavy and marked/unhealthy or fault-injection oriented, so CI runtime and host capacity matter.
- Object-store and filesystem APIs must remain behaviorally aligned for mixed operations.

## Test Signals
Signals come from chaos-test completion, propagated future exceptions, JUnit assertions in `LoadBucket`, mini-cluster readiness waits, and generated test reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/loadgenerators/LoadBucket.java -->
