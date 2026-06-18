# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodesResponse.java

## Purpose
Datanode list response carrying total count, datanode metadata rows, and optional failed-node error details.

## Important APIs, Types, And Functions
declares `DatanodesResponse`; key fields include `totalCount`, `datanodes`, `failedNodeErrorResponseMap`; important methods include `getTotalCount`, `getDatanodes`, `getFailedNodeErrorResponseMap`, `setFailedNodeErrorResponseMap`.

## Control Flow
Constructors initialize the error map to empty and `JsonInclude.NON_EMPTY` hides it until failures are present.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, Jackson inclusion. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover normal list output and partial-failure maps from decommission/remove flows.
