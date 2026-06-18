# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodeMetrics.java

## Purpose
Small DTO for decommission-related datanode metrics: start time, unclosed pipelines, under-replicated containers, and unclosed containers.

## Important APIs, Types, And Functions
declares `DatanodeMetrics`; key fields include `decommissionStartTime`, `numOfUnclosedPipelines`, `numOfUnderReplicatedContainers`, `numOfUnclosedContainers`; important methods include `getDecommissionStartTime`, `setDecommissionStartTime`, `getNumOfUnclosedPipelines`, `setNumOfUnclosedPipelines`, `getNumOfUnderReplicatedContainers`, `setNumOfUnderReplicatedContainers`, `getNumOfUnclosedContainers`, `setNumOfUnclosedContainers`.

## Control Flow
Mutable setters let decommission status code attach metrics collected from SCM/Recon services.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should check JSON names and numeric type expectations, especially double-valued container metrics.
