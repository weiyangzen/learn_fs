# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerStateCounts.java

## Purpose
Simple mutable holder for total, missing, open, and deleted container counts used when building cluster state summaries.

## Important APIs, Types, And Functions
declares `ContainerStateCounts`; key fields include `totalContainerCount`, `missingContainerCount`, `openContainersCount`, `deletedContainersCount`; important methods include `getTotalContainerCount`, `setTotalContainerCount`, `getMissingContainerCount`, `setMissingContainerCount`, `getOpenContainersCount`, `setOpenContainersCount`, `getDeletedContainersCount`, `setDeletedContainersCount`.

## Control Flow
No validation or derived values; callers are responsible for computing the counts consistently from SCM/recon tables.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should focus on services that populate it rather than this bean, plus zero/default behavior.
