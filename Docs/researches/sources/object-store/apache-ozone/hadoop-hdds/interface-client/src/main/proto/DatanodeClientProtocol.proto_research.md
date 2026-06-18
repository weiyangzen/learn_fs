<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/DatanodeClientProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/DatanodeClientProtocol.proto

## Purpose

Defines datanode container command contracts for client and intra-datanode traffic, including streaming command exchange, container copy/download/upload, block and chunk IO, checksum trees, small-file helpers, and container metadata reports.

## Important APIs, types, and functions

Package: `hadoop.hdds.datanode`. Imports: none. Important declarations include `DatanodeBlockID, KeyValue, ContainerCommandRequestProto, ContainerCommandResponseProto, ContainerDataProto, Container2BCSIDMapProto, CreateContainerRequestProto, CreateContainerResponseProto, ReadContainerRequestProto, ReadContainerResponseProto, UpdateContainerRequestProto, UpdateContainerResponseProto, DeleteContainerRequestProto, DeleteContainerResponseProto, ListContainerRequestProto, ListContainerResponseProto, CloseContainerRequestProto, CloseContainerResponseProto, BlockData, PutBlockRequestProto, PutBlockResponseProto, FinalizeBlockRequestProto, FinalizeBlockResponseProto, GetBlockRequestProto, GetBlockResponseProto, DeleteBlockRequestProto, GetCommittedBlockLengthRequestProto, GetCommittedBlockLengthResponseProto, ...`. RPC methods: send(stream ContainerCommandRequestProto -> stream ContainerCommandResponseProto), download(CopyContainerRequestProto -> stream CopyContainerResponseProto), upload(stream SendContainerRequest -> SendContainerResponse).

## Control flow

Clients send ContainerCommandRequestProto values tagged with Type; the datanode responds with ContainerCommandResponseProto carrying Result and an operation-specific payload. The bidirectional send RPC handles ordinary xceiver commands, while download and upload stream raw container transfer messages for replication and repair.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

The protocol mixes metadata, data buffers, checksums, tokens, and container/block lifecycle actions. Compatibility risk is high around enum ordinal changes, required fields, token/signature fields, checksum versioning, and streaming backpressure.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/DatanodeClientProtocol.proto -->
