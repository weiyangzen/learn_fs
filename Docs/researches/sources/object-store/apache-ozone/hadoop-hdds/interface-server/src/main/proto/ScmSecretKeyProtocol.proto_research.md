<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmSecretKeyProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmSecretKeyProtocol.proto

## Purpose

Defines SCM secret-key management RPCs for current key retrieval, specific key lookup, key listing, and check-and-rotate operations.

## Important APIs, types, and functions

Package: `hadoop.hdds.security.symmetric`. Imports: `hdds.proto`. Important declarations include `SCMSecretKeyRequest, SCMSecretKeyResponse, ManagedSecretKey, SCMGetSecretKeyRequest, SCMGetCheckAndRotateRequest, SCMGetCurrentSecretKeyResponse, SCMGetSecretKeyResponse, SCMSecretKeysListResponse, SCMGetCheckAndRotateResponse, Type, Status, SCMSecretKeyProtocolService`. RPC methods: submitRequest(SCMSecretKeyRequest -> SCMSecretKeyResponse).

## Control flow

Requests use SCMSecretKeyRequest with a Type enum and response envelope with Status. ManagedSecretKey embeds SecretKeyProto from hdds.proto for durable key metadata.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

Secret-key material is security-sensitive. Rotation races, stale current-key reads, and over-broad list access are server-side risks that need integration tests.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmSecretKeyProtocol.proto -->
