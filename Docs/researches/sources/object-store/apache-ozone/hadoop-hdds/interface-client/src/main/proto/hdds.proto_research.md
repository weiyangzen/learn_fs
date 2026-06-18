<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/hdds.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/hdds.proto

## Purpose

Provides common HDDS protobuf types shared across client, server, and admin interfaces: datanode and SCM identity, node state, pipeline and container metadata, replication configuration, tokens/secrets, reports, topology, compaction, deleted-block, and disk-balancer structures.

## Important APIs, types, and functions

Package: `hadoop.hdds`. Imports: none. Important declarations include `UUID, DatanodeIDProto, DatanodeDetailsProto, ExtendedDatanodeDetailsProto, MoveDataNodePairProto, OzoneManagerDetailsProto, ScmNodeDetailsProto, NodeDetailsProto, Port, PipelineID, ContainerID, Pipeline, KeyValue, Node, NodePool, DatanodeUsageInfoProto, ContainerInfoProto, ContainerWithPipeline, GetScmInfoRequestProto, GetScmInfoResponseProto, AddScmRequestProto, AddScmResponseProto, RemoveScmRequestProto, RemoveScmResponseProto, ECReplicationConfig, DefaultReplicationConfig, ExcludeListProto, ContainerBlockID, ...`. RPC methods: none.

## Control flow

Other protocol files import this file and embed its messages as stable wire-level building blocks. There is no executable control flow; behavior comes from generated Java builders and from consumers that interpret lifecycle enums, IDs, token bytes, and repeated metadata lists.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

Because this file is foundational, changing tags or enum values can break many modules. Optional identity, topology, and security fields require careful presence checks, and repeated maps encoded as KeyValue-style messages can carry duplicate keys unless consumers normalize them.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/hdds.proto -->
