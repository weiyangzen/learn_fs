# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyMetadata.java

## Purpose
Detailed key metadata response for container-to-key and key lookup APIs, including volume/bucket/key path, data size, versions, block ids, and timestamps.

## Important APIs, Types, And Functions
declares `KeyMetadata`, `ContainerBlockMetadata`; key fields include `volume`, `bucket`, `key`, `completePath`, `dataSize`, `versions`, `blockIds`, `creationTime`, `modificationTime`, `containerID`; important methods include `getVolume`, `getBucket`, `getKey`, `getDataSize`, `getCreationTime`, `getModificationTime`, `getVersions`, `getBlockIds`, `getCompletePath`, `getContainerID`, `getLocalID`.

## Control Flow
Maintains sorted version/block maps with nested `ContainerBlockMetadata` rows for container/local block IDs.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with JAXB/XML. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify version ordering, block-id grouping, complete path construction, and timestamp serialization.
