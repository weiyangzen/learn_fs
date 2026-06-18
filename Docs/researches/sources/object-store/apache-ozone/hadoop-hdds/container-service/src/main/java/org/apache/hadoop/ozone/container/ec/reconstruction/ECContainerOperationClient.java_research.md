# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECContainerOperationClient.java

## Purpose
`ECContainerOperationClient` wraps the container-level RPC operations needed by erasure-coded offline reconstruction. It centralizes single-datanode pipeline construction and lifecycle management for list, create recovering container, close container, read-state-then-delete, and delete operations.

## Important APIs and Types
Constructors accept either an existing `XceiverClientManager` or a `ConfigurationSource` plus `CertificateClient`. `listBlock` returns `BlockData[]` for a container on a datanode. `closeContainer`, `deleteContainerInState`, and `createRecoveringContainer` delegate to `ContainerProtocolCalls`. `singleNodePipeline` builds a closed `Pipeline` containing one `DatanodeDetails` and a replica-index map.

## Control Flow
Each RPC method acquires a client from `XceiverClientManager` using a single-node pipeline, performs the container protocol call, and releases the client in a `finally` block with `invalidateClient=false`. `createClientManager` installs a `ClientTrustManager` only when security is enabled and configures a small cached client manager. `deleteContainerInState` first calls `readContainer`, checks the current container state against the caller-provided acceptable state set, and only then sends `deleteContainer`.

## State and Persistence
The only long-lived state is the `XceiverClientManager` and its underlying client cache. The class does not write local disk state. Remote operations change container state on target datanodes: creating RECOVERING replicas, closing containers, or deleting acceptable-state replicas.

## Dependencies and Integration Points
`ECReconstructionCoordinator` uses this client for source block listing and target container lifecycle. It depends on SCM pipeline/client classes, datanode protocol protobufs, security certificate/trust-manager classes, Ozone security detection, and `BlockData` protobuf conversion. Integration tests in `TestContainerCommandsEC` use this class directly for EC container command validation.

## Risks and Test Signals
`listBlock` maps protobuf conversion failures to `null` array entries, which can later surprise callers unless they tolerate missing block data. `deleteContainerInState` explicitly documents a race between read and delete: the check is not atomic with deletion, so callers must restrict use to contexts where deleting a newly changed container is acceptable. Test signals include EC reconstruction integration tests, direct `ECContainerOperationClient` use in `TestContainerCommandsEC`, and cleanup-on-failure scenarios that exercise state-gated deletion.
