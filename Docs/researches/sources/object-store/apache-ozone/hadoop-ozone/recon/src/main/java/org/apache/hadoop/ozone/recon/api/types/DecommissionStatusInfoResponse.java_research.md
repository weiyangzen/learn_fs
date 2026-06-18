# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DecommissionStatusInfoResponse.java

## Purpose
Response object for decommission status of a single datanode, including node details, decommission metrics, and container groups by status/category.

## Important APIs, Types, And Functions
declares `DecommissionStatusInfoResponse`; key fields include `dataNodeDetails`, `datanodeMetrics`, `containers`; important methods include `getDataNodeDetails`, `setDataNodeDetails`, `getDatanodeMetrics`, `setDatanodeMetrics`, `getContainers`, `setContainers`.

## Control Flow
Plain mutable DTO populated by decommission APIs from HDDS `DatanodeDetails`, `DatanodeMetrics`, and container ID maps.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify JSON names and container map grouping for under-replicated, unclosed, or related decommission categories.
