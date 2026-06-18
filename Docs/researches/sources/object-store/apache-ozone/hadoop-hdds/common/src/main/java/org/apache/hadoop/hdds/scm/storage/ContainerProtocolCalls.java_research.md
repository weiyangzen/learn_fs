# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/storage/ContainerProtocolCalls.java

## Purpose
Static client-side facade for datanode container protocol RPCs. It builds `ContainerCommandRequestProto` messages, attaches tokens and trace IDs, chooses datanodes from a `Pipeline`, sends sync or async commands through `XceiverClientSpi`, and validates responses.

## Important APIs and types
- Read/list APIs: `listBlock`, `getBlock`, `getCommittedBlockLength`, `readChunk`, `readContainer`, `readSmallFile`, `getContainerChecksumInfo`, `getBlockFromAllNodes`, `readContainerFromAllNodes`, and `buildReadBlockCommandProto`.
- Write/modify APIs: `putBlockAsync`, `finalizeBlock`, `getPutBlockRequest`, `writeChunkAsync`, `writeSmallFile`, `createRecoveringContainer`, `createContainer`, `deleteContainer`, and `closeContainer`.
- Routing helpers: `tryEachDatanode`, `getDatanodeBlockID`, and error-message helpers.
- Validation helpers: `validateContainerResponse`, `toValidatorList`, and the default validator list.

## Control flow and state
The class is stateless with a static immutable default validator list. Most methods build command-specific request payloads, attach encoded block/container tokens when provided, optionally attach `TracingUtil.exportCurrentSpan()`, and call `sendCommand` or `sendCommandAsync`.

`tryEachDatanode` repeatedly selects the closest non-excluded datanode, runs the operation, and retries another datanode on `IOException`. It does not retry when the result is `BLOCK_TOKEN_VERIFICATION_FAILED`, because another datanode cannot fix an expired or invalid token. It records tracing events for failed datanode attempts.

Read paths differ by command. `getBlock` and `readChunk` retry across pipeline nodes and apply EC replica indexes to `DatanodeBlockID`. `readChunk` verifies the returned data length, supporting both legacy `data` and V1 `dataBuffers`. Several metadata-style calls use `getFirstNode` or `getClosestNode` without retry.

Write paths usually target the first pipeline node, relying on the underlying client/pipeline replication semantics. `writeSmallFile` builds a synthetic chunk with CRC32 checksum and overwrite metadata. Container create/delete/close/read APIs propagate trace ID and tokens and rely on validators for error conversion.

## Dependencies and integration points
The class integrates `XceiverClientSpi`, `XceiverClientReply`, `Pipeline`, `DatanodeDetails`, `BlockID`, `ContainerProtos`, checksum utilities, Hadoop tokens, OpenTelemetry spans, and SCM storage exceptions. It is the client counterpart to datanode command handlers that use `ContainerCommandResponseBuilders`.

## Risks and test signals
Tests should exercise request shape for every command type, token inclusion, trace propagation, EC replica-index handling, retry/exclusion logic, no-retry token failure, read length validation, V0/V1 data length calculation, all-node command response maps, and validator exception mapping. Watch for builder reuse in retry loops, commands that do not retry across nodes, and async write behavior when the first node is unavailable. `validateContainerResponse` maps only selected result codes to specialized exceptions; all others become generic `StorageContainerException`.
