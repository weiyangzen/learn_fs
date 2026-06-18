<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/InterSCMProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/InterSCMProtocol.proto

## Purpose

Defines inter-SCM checkpoint transfer messages used by a follower SCM to copy a leader's DB checkpoint.

## Important APIs, types, and functions

Package: `default`. Imports: none. Important declarations include `CopyDBCheckpointRequestProto, CopyDBCheckpointResponseProto, InterSCMProtocolService`. RPC methods: download(CopyDBCheckpointRequestProto -> stream CopyDBCheckpointResponseProto).

## Control flow

The CopyDBCheckpoint RPC accepts a request and returns a response with checkpoint location/status data; actual filesystem transfer and persistence occur in the server implementation.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

Checkpoint copy must coordinate with leadership, snapshot consistency, and secure peer authentication. The proto does not encode those guarantees.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/InterSCMProtocol.proto -->
