<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/storage/TestCommitWatcher.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/storage/TestCommitWatcher.java

Purpose: Tests `CommitWatcher` buffer-release behavior after successful Ratis commits and after watch failures.

Important APIs and types: Uses `MiniOzoneCluster`, `XceiverClientManager`, `XceiverClientRatis`, `CommitWatcher`, `BufferPool`, `ChunkBuffer`, `XceiverClientReply`, `ContainerTestHelper`, `BlockID`, Ratis client/server timeout configs, `HddsClientUtils.checkForException`, and Ratis exceptions including `RaftRetryFailureException`, `TimeoutIOException`, `AlreadyClosedException`, and `NotReplicatedException`.

Control flow: Setup configures large block/chunk/flush sizes, disables checksums, stretches SCM node failure timers to keep pipelines alive, and creates a volume/bucket to initialize the cluster. Each test allocates a Ratis three container, acquires an xceiver client, writes chunks asynchronously, sends put-block requests, stores reply log indexes with buffers in `CommitWatcher`, waits for put-block futures, and watches commit indexes. The exception test shuts down two pipeline nodes before watching a future index to force an actual Ratis watch call and error.

State and persistence behavior: Runtime state includes buffer-pool allocation, `CommitWatcher` commit-index map, total acknowledged data length, and the Ratis client's replicated minimum commit index. Persistent cluster state includes container/block writes sent to datanodes.

Dependencies and integration points: Integrates stream buffer management, Ratis async write and watch APIs, SCM container allocation, xceiver client acquisition/refcounting, client timeout configuration, and datanode shutdown failure modes.

Risks: Exception behavior is intentionally broad because different Ratis failure paths can surface under timing. The tests track but do not assert the local `length` variable. Buffer cleanup depends on `finally` clearing the pool. Shutting down two nodes in a five-node cluster targets a three-node pipeline and assumes they are members.

Test signals: Signals include xceiver refcount one, commit-index map size two after put-block futures, first watch removing the first log index and acknowledging at least one chunk, last watch removing all entries and acknowledging two chunks, watch failure unwrapping to one accepted Ratis exception type, and post-failure map/ack length matching whether the target log index was replicated.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/storage/TestCommitWatcher.java -->
