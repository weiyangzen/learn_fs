<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/SCMRatisProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/SCMRatisProtocol.proto

## Purpose

Defines the Ratis replication request/response envelope used for SCM HA state-machine commands.

## Important APIs, types, and functions

Package: `default`. Imports: none. Important declarations include `Method, MethodArgument, ListArgument, SCMRatisRequestProto, SCMRatisResponseProto, RequestType`. RPC methods: none.

## Control flow

SCM serializes state-changing commands into SCMRatisRequestProto and receives SCMRatisResponseProto after the replicated state machine applies them.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

All persisted SCM HA mutations depend on deterministic serialization and replay. Adding fields requires careful default handling so old log entries still apply.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/SCMRatisProtocol.proto -->
