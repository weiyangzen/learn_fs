<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/SCMUpdateProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/SCMUpdateProtocol.proto

## Purpose

Defines a streaming update service where clients subscribe to SCM update channels, receive update events, and unsubscribe when no longer interested.

## Important APIs, types, and functions

Package: `hadoop.hdds.scm`. Imports: none. Important declarations include `CRLInfoProto, ClientId, SubscribeRequest, SubscribeResponse, UpdateRequest, UpdateResponse, CRLUpdateRequest, CRLUpdateResponse, UnsubscribeRequest, UnsubscribeResponse, Type, SCMUpdateService`. RPC methods: subscribe(SubscribeRequest -> SubscribeResponse), updateStatus(stream UpdateRequest -> stream UpdateResponse), unsubscribe(UnsubscribeRequest -> UnsubscribeResponse).

## Control flow

The service exposes subscribe, updateStatus, and unsubscribe style messages. It is a transport contract for server-pushed SCM state rather than persistent state itself.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

Streaming protocols need backpressure, subscriber cleanup, and versioned payload handling. Missing unsubscribe or failed status handling can leak server-side subscriber state.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/SCMUpdateProtocol.proto -->
