<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/ProtobufRpcEngine.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/ProtobufRpcEngine.proto

## Purpose

Defines Hadoop-compatible IPC framing metadata for protobuf RPC calls, including connection user/protocol context, request method headers, request and response status headers, tracing/caller context, and SASL negotiation messages.

## Important APIs, types, and functions

Package: `hadoop.common`. Imports: none. Important declarations include `RequestHeaderProto`. RPC methods: none.

## Control flow

Generated classes are used by the RPC engine before service-level messages are dispatched. Request headers identify rpc kind, method, client ID, retry state, trace info, and caller context; response headers carry call ID, status, exception metadata, server IP, and SASL state.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

These messages sit below application protocols, so incompatible tag or enum changes can break every RPC. Security-sensitive fields such as SASL auth lists and effective user names must be validated by the transport layer rather than trusted because they are serialized input.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/ProtobufRpcEngine.proto -->
