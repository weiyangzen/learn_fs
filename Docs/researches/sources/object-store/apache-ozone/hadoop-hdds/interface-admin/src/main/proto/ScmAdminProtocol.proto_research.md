<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-admin/src/main/proto/ScmAdminProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-admin/src/main/proto/ScmAdminProtocol.proto

## Purpose

Defines the SCM administrative protobuf envelope used by Ozone clients to query and mutate container, node, pipeline, safe-mode, replication-manager, deleted-block, upgrade, container-token, container-balancer, SCM decommission, metrics, reconcile, and suppression operations through one submitRequest RPC.

## Important APIs, types, and functions

Package: `hadoop.hdds.container`. Imports: `hdds.proto`. Important declarations include `ScmContainerLocationRequest, ScmContainerLocationResponse, ContainerRequestProto, ContainerResponseProto, GetContainerRequestProto, GetContainerResponseProto, GetContainerWithPipelineRequestProto, GetContainerWithPipelineResponseProto, GetContainerReplicasRequestProto, GetContainerReplicasResponseProto, GetContainerWithPipelineBatchRequestProto, GetExistContainerWithPipelinesInBatchRequestProto, GetSafeModeRuleStatusesRequestProto, SafeModeRuleStatusProto, GetSafeModeRuleStatusesResponseProto, GetContainerWithPipelineBatchResponseProto, GetExistContainerWithPipelinesInBatchResponseProto, SCMListContainerIDsRequestProto, SCMListContainerIDsResponseProto, SCMListContainerRequestProto, SCMListContainerResponseProto, SCMDeleteContainerRequestProto, SCMDeleteContainerResponseProto, SCMCloseContainerRequestProto, SCMCloseContainerResponseProto, NodeQueryRequestProto, NodeQueryResponseProto, SingleNodeQueryRequestProto, ...`. RPC methods: submitRequest(ScmContainerLocationRequest -> ScmContainerLocationResponse).

## Control flow

Callers fill ScmContainerLocationRequest with a Type enum and exactly one matching request body. The server dispatches on cmdType and returns ScmContainerLocationResponse with a Status, optional message, traceID, and the corresponding response body. The nested request/response messages carry no persistence themselves; they serialize administrative intent and SCM state snapshots.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

The main risk is envelope drift: adding a Type without a matching optional field, response field, dispatcher branch, or compatibility test yields requests that compile but fail at runtime. Many fields are optional proto2 fields, so callers must distinguish absent values from default values.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-admin/src/main/proto/ScmAdminProtocol.proto -->
