# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/MoveDataNodePair.java

## Purpose

`MoveDataNodePair` represents a source and target datanode for container movement decisions.

## Important APIs, Types, and Functions

It stores final `DatanodeDetails src` and `tgt`, provides getters, `getProtobufMessage(int)`, `getFromProtobuf`, and a static RocksDB `Codec<MoveDataNodePair>` built with `DelegatedCodec` and `Proto2Codec`.

## Control Flow

Serialization converts both datanodes to protobuf at the requested client version. Deserialization requires a non-null proto and converts both endpoints back to `DatanodeDetails`.

## State and Persistence Behavior

Object state is immutable references. The codec persists move pairs in SCM metadata, specifically the move table keyed by container ID.

## Dependencies and Integration Points

It integrates datanode identity, `MoveDataNodePairProto`, client-version-aware protobuf conversion, and SCM metadata tables.

## Risks and Test Signals

There is no explicit null validation for constructor arguments, so serialization can fail later. Tests should cover codec round trips, client version compatibility, null proto rejection, and equality expectations in table consumers.
