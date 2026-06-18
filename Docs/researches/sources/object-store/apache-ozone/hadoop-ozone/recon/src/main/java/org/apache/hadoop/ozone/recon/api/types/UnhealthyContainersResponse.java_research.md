# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/UnhealthyContainersResponse.java

## Purpose
Paged response and summary counters for unhealthy containers across missing, under-replicated, over-replicated, mis-replicated, and replica-mismatch states.

## Important APIs, Types, And Functions
declares `UnhealthyContainersResponse`; key fields include `missingCount`, `underReplicatedCount`, `overReplicatedCount`, `misReplicatedCount`, `replicaMismatchCount`, `firstKey`, `lastKey`, `containers`; important methods include `setSummaryCount`, `getMissingCount`, `getUnderReplicatedCount`, `getOverReplicatedCount`, `getMisReplicatedCount`, `getReplicaMismatchCount`, `getLastKey`, `getFirstKey`, `getContainers`, `setFirstKey`, `setLastKey`.

## Control Flow
`setSummaryCount` maps generated schema state enums to the matching counter; first/last keys support pagination.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover every enum branch in `setSummaryCount`, cursor fields, and row collection output.
