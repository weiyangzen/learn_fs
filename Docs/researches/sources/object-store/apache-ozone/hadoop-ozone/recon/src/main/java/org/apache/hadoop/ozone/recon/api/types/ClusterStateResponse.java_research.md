# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ClusterStateResponse.java

## Purpose
Top-level Recon cluster state response aggregating pipeline, datanode, storage, container, namespace, deletion backlog, and service-id counters.

## Important APIs, Types, And Functions
declares `ClusterStateResponse`, `Builder`; key fields include `pipelines`, `totalDatanodes`, `healthyDatanodes`, `storageReport`, `containers`, `missingContainers`, `openContainers`, `deletedContainers`, `volumes`, `buckets`; important methods include `newBuilder`, `build`, `getPipelines`, `getTotalDatanodes`, `getHealthyDatanodes`, `getStorageReport`, `getContainers`, `getVolumes`, `getMissingContainers`, `getOpenContainers`, `getDeletedContainers`, `getBuckets`.

## Control Flow
The builder initializes all counters to zero, requires a non-null `ClusterStorageReport` at build time, and copies mutable builder state into a final response object.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover required storage report validation, default zero counters, deleted-dir/key-pending fields, and HA service-id serialization.
