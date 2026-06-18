<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerProtocol.proto

## Purpose

Defines the client-facing SCM server protocol for SCM info, block allocation/deletion, container queries, pipeline operations, safe mode, replication manager status, and related storage-control requests.

## Important APIs, types, and functions

Package: `hadoop.hdds.block`. Imports: `hdds.proto`. Important declarations include `SCMBlockLocationRequest, SCMBlockLocationResponse, UserInfo, AllocateScmBlockRequestProto, DeleteScmKeyBlocksRequestProto, KeyBlocks, DeleteScmKeyBlocksResponseProto, DeleteKeyBlocksResultProto, DeleteScmBlockResult, AllocateBlockResponse, AllocateScmBlockResponseProto, SortDatanodesRequestProto, SortDatanodesResponseProto, GetClusterTreeRequestProto, GetClusterTreeResponseProto, Type, Status, Result, ScmBlockLocationProtocolService`. RPC methods: send(SCMBlockLocationRequest -> SCMBlockLocationResponse).

## Control flow

A request envelope selects the command type and carries the matching request. The server returns a response envelope with status and matching payload, backed by SCM managers that persist container, block, pipeline, and node metadata.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

Envelope-field mismatches, optional field absence, and enum compatibility are the main protocol risks. Block/container operations also depend on SCM state machines and must avoid issuing stale pipeline or container information.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerProtocol.proto -->
