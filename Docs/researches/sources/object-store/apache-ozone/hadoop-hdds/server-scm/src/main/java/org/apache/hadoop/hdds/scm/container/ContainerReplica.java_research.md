<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReplica.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReplica.java

## Purpose
Models SCM's in-memory view of a single container replica on a datanode, including replica state, current and origin datanode identity, replica index, BCSID, key count, bytes used, emptiness, and checksums.

## Important APIs, Types, And Functions
`ContainerReplica` is immutable and comparable. Accessors expose container ID, datanode details, origin datanode ID, replica state, sequence ID, key count, bytes used, empty flag, checksums, data checksum, and replica index. `newBuilder()` and `toBuilder()` support construction and copy-modification. Equality and hash code use only `containerID` and `datanodeDetails`; ordering compares those same fields.

## Control Flow
Report handlers construct instances from datanode `ContainerReplicaProto` records and pass them to `ContainerManager.updateContainerReplica` or remove methods. Builder `build()` defaults checksums to `ContainerChecksums.unknown()` when unset.

## State And Persistence
The object is in-memory value state. It is generally stored in SCM's `ContainerStateMap` replica sets and rebuilt from reports after restart. Container metadata persistence is separate from this replica value.

## Dependencies And Integration Points
Depends on `DatanodeDetails`, `DatanodeID`, protobuf replica state, `ContainerChecksums`, and Apache Commons builder helpers. It is consumed by report handling, replication manager, balancer, close command fallback, and placement validation.

## Risks And Test Signals
Because equality ignores state, index, size, sequence ID, and checksum, sets treat a container on a datanode as one replaceable location record. That is intentional for update semantics but risky if multiple replicas of the same container/index could appear on one datanode. Tests should cover builder defaults, origin fallback to current datanode, equality semantics, ordering, `toBuilder`, and checksum propagation from reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReplica.java -->
