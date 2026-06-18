## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestPushReplicator.java

Purpose: Tests push-based container replication status handling, compression propagation, and upload stream cleanup.

Important APIs/types/functions: `PushReplicator.replicate`, `ContainerReplicationSource.copyData`, `ContainerUploader.startUpload`, `CopyContainerCompression`, `ReplicationTask`, and `SpyOutputStream`.

Control flow: Helper builds mocked source/uploader and captures the completion future and compression. Success parameterizes all compression values, completes the future normally, and expects task `DONE`. Failure completes the future exceptionally, or throws during copy, and expects task `FAILED`. Every path asserts the output stream closes exactly once.

State and persistence behavior: No persistent data; stream closure and task status are the state under test.

Dependencies and integration points: Covers config-to-compression handoff between push replicator, upload stream, and data source.

Risks and test signals: Does not cover partial data writes or remote backpressure. Strong signal for cleanup and status correctness.
