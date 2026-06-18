# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestCommandQueue.java

Purpose: verifies `CommandQueue` maintains per-datanode command summary counts and clears them when commands are drained or the queue is cleared.

Important APIs and types: constructs `CommandQueue`, `CloseContainerCommand`, `CreatePipelineCommand`, and `ReplicateContainerCommand`. Uses `DatanodeID` keys and protobuf `SCMCommandProto.Type` values. A low-priority replication command is also enqueued to ensure summary counting is by command type, not priority.

Control flow: the test adds several commands to two datanodes, checks unknown datanode counts return zero, validates per-type counts and summary map for datanode one, then calls `getCommand(datanode1ID)` and verifies datanode one counts are reset while datanode two counts remain. Finally, `clear()` zeroes all remaining counts.

State and persistence: state is fully in-memory in the command queue. No external resources are used.

Integration points and risks: `CommandQueue` feeds commands returned on datanode heartbeats and exposes summary metrics/inspection. This test protects count bookkeeping when duplicate commands and multiple command types are queued. It does not cover concurrent access, command ordering details, or queue size limits.
