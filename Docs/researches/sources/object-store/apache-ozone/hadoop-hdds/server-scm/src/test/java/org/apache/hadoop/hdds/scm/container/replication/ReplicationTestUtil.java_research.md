# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationTestUtil.java

Purpose: `ReplicationTestUtil` is a shared test helper for SCM replication manager tests. It creates container metadata, replica sets, simple placement policies, and Mockito command-capture stubs for replication, reconstruction, delete, and generic datanode commands.

Important APIs and types: It exposes many static helpers around `ContainerReplica`, `ContainerInfo`, `ContainerID`, `ReplicationConfig`, `PlacementPolicy`, `SCMCommonPlacementPolicy`, `ContainerPlacementStatusDefault`, `ReplicateContainerCommand`, `DeleteContainerCommand`, `ReconstructECContainersCommand`, `SCMCommand`, `CommandTargetOverloadedException`, and `NotLeaderException`.

Control flow: Replica helpers build sets from replica indexes, operational states, replica states, origins, sequence IDs, key counts, and bytes used. Container helpers delegate to `TestContainerInfo.newBuilderForTest`. Placement helpers return anonymous `SCMCommonPlacementPolicy` implementations that either pick random nodes, return a specific node, or throw configured SCM exceptions. Mockito helpers install `doAnswer` callbacks that convert replication-manager method calls into command objects stored in a caller-provided set, optionally simulating one overload failure.

State and persistence behavior: There is no persistence. Helpers mutate `DatanodeDetails` persisted operational state when creating replicas and collect commands in caller-owned sets. Some helpers assert expected required replication space from configuration during policy calls.

Dependencies and integration points: This utility is widely used by replication manager, handler, and balancer tests to avoid repeated boilerplate and to make command-sending behavior observable without a running SCM or datanode.

Risks: Because it centralizes test construction, defaults such as sequence ID, key count, bytes used, `empty` flag, and origin handling can shape many tests. Some generated policies intentionally ignore real topology. Overloaded-command helpers only throw once by flipping an `AtomicBoolean`.

Test signals: Consumers observe constructed replica membership, op state/index/state fields, container metadata fields, expected SCMException result codes, and captured command objects with target datanodes and replica indexes.
