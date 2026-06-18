<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerDatanodeHeartbeatProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerDatanodeHeartbeatProtocol.proto

## Purpose

Defines SCM's datanode heartbeat protocol, including heartbeat request/response envelopes, node/container/pipeline/incremental reports, commands sent from SCM to datanodes, and command status feedback.

## Important APIs, types, and functions

Package: `hadoop.hdds`. Imports: `hdds.proto`. Important declarations include `SCMDatanodeRequest, SCMDatanodeResponse, LayoutVersionProto, SCMVersionRequestProto, SCMVersionResponseProto, SCMRegisterRequestProto, SCMRegisteredResponseProto, SCMHeartbeatRequestProto, CommandQueueReportProto, SCMHeartbeatResponseProto, SCMNodeAddressList, NodeReportProto, StorageReportProto, MetadataStorageReportProto, ContainerReportsProto, IncrementalContainerReportProto, ContainerReplicaProto, CommandStatusReportsProto, CommandStatus, ContainerActionsProto, ContainerAction, PipelineReport, PipelineReportsProto, PipelineActionsProto, ClosePipelineInfo, PipelineAction, SCMCommandProto, ReregisterCommandProto, ...`. RPC methods: submitRequest(SCMDatanodeRequest -> SCMDatanodeResponse).

## Control flow

Datanodes send SCMHeartbeatRequestProto with reports and command status; SCM replies with SCMHeartbeatResponseProto containing commands such as reregister, delete blocks, close containers, replicate, delete container, finalize upgrade, refresh volume usage, and other operational directives.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

This is a high-volume operational protocol. Risks include oversized reports, command-id correlation bugs, stale layout/version information, replayed command status, and compatibility of new command payloads with older datanodes.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerDatanodeHeartbeatProtocol.proto -->
