# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReplicaInfo.java

## Purpose
Client-facing container replica DTO populated from SCM replica protobufs. It exposes container ID, replica state, datanode, origin datanode, sequence ID, key count, bytes used, replica index, and checksum.

## Important APIs, Types, And Functions
`fromProto(HddsProtos.SCMContainerReplicaProto)` maps protobuf fields into a builder. Getters expose all fields. Nested `Builder` mutates a private subject and returns it from `build()`. `dataChecksum` uses `JsonUtils.ChecksumSerializer`.

## Control Flow
SCM/API code converts replica protobufs to this DTO before JSON or client responses. Optional `replicaIndex` defaults to `-1` when absent.

## State And Persistence
The object is mutable during builder use and then conventionally immutable. It is a transient API view, not the authoritative persisted replica state.

## Dependencies And Integration Points
Depends on datanode details/ID, HddsProtos, Jackson serializer, and HDDS JSON utilities. Integrated by SCM container report/list APIs and Recon/admin clients.

## Risks And Test Signals
The builder returns the same subject object and does not validate required fields. Tests should cover protobuf mapping, absent replica index, checksum JSON formatting, and place-of-birth UUID parsing.
