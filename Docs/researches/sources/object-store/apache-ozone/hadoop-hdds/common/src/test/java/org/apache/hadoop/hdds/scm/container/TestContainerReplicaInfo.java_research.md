# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerReplicaInfo.java

## Purpose
Tests construction of `ContainerReplicaInfo` from protobuf replica metadata.

## Important APIs, types, and functions
- Uses `DatanodeDetails`, `MockDatanodeDetails`, `HddsProtos.ContainerReplicaProto`, and replica state fields.
- Covers object creation with and without an explicit EC replica index.

## Control flow
The tests build protobuf representations of container replicas, convert them to Java objects, and assert datanode UUID, container ID, state, sequence ID, bytes used, key count, and optional replica index.

## State and persistence behavior
The protobuf is treated as serialized replica state, but no external store is used.

## Dependencies and integration points
Replica info is consumed by SCM container reports, replication manager decisions, and EC placement logic.

## Risks and test signals
Incorrect protobuf mapping can hide replica index or datanode identity, especially for EC containers. These tests signal accurate conversion from report wire format.
