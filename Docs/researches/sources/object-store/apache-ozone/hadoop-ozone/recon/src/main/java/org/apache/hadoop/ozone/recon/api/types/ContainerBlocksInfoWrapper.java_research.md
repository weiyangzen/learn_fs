# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerBlocksInfoWrapper.java

## Purpose
Wrapper for a container id, local block ids, local id count, and transaction id used by Recon container-block inspection APIs.

## Important APIs, Types, And Functions
declares `ContainerBlocksInfoWrapper`; key fields include `containerID`, `localIDList`, `localIDCount`, `txID`; important methods include `getContainerID`, `setContainerID`, `getLocalIDList`, `setLocalIDList`, `getLocalIDCount`, `setLocalIDCount`, `getTxID`, `setTxID`.

## Control Flow
Default construction creates an empty local-id list, container/count zero, and txID -1; setters are plain mutable DTO accessors.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, Jackson inclusion. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should check omitted default fields from `JsonInclude`, non-empty block list serialization, and txID sentinel behavior.
