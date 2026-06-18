# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/PushReplicator.java

Purpose: implements push replication by streaming a local container archive directly to a target datanode.

Important APIs and functions: `replicate(ReplicationTask)` reads the target from the task, resolves configured compression, calls `source.prepare`, opens an upload stream through `ContainerUploader`, wraps it in `CountingOutputStream`, copies source data into it, waits for the upload future, records byte count, and marks the task done or failed.

Control flow and state: the method is synchronous and executor-thread blocking. The upload future captures remote import success or failure. Cleanup closes the output stream with `IOUtils.cleanupWithLogger`, even if the stream was already closed by an error.

Dependencies and integration: used for `ReplicateContainerCommand` instances carrying a target datanode. It depends on `ContainerReplicationSource`, `ContainerUploader`, compression config, and `ReplicationTask` status fields.

Risks and test signals: future wait can block if the response observer never completes. Tests should cover target missing/null handling, source copy exceptions, upload open failures, remote error completion, transferred byte accounting on partial failure, and cleanup idempotence.
