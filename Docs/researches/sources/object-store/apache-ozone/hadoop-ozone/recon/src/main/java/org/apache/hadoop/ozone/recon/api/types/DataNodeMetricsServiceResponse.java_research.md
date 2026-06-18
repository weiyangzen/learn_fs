# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DataNodeMetricsServiceResponse.java

## Purpose
Response from datanode metrics collection, especially pending deletion byte metrics per datanode plus collection status and failure counts.

## Important APIs, Types, And Functions
declares `are`, `DataNodeMetricsServiceResponse`, `Builder`; key fields include `status`, `totalPendingDeletionSize`, `pendingDeletionPerDataNode`, `totalNodesQueried`, `totalNodeQueryFailures`, `status`, `totalPendingDeletionSize`, `pendingDeletion`, `totalNodesQueried`, `totalNodeQueryFailures`; important methods include `getStatus`, `getTotalPendingDeletionSize`, `getPendingDeletionPerDataNode`, `getTotalNodesQueried`, `getTotalNodeQueryFailures`, `newBuilder`, `setStatus`, `setTotalPendingDeletionSize`, `setPendingDeletion`, `setTotalNodesQueried`, `setTotalNodeQueryFailures`, `build`.

## Control Flow
Builder copies metric status, totals, per-node rows, queried count, and query failure count without extra validation.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should simulate full, partial, and failed metric collection statuses and verify failure metadata is exposed.
