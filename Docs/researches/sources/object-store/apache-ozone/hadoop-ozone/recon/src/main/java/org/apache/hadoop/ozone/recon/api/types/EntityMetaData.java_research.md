# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/EntityMetaData.java

## Purpose
Metadata row for namespace entity listings and heatmap inputs: value label, child/entity count, and read access count.

## Important APIs, Types, And Functions
declares `EntityMetaData`; key fields include `val`, `count`, `readAccessCount`; important methods include `getVal`, `setVal`, `getCount`, `setCount`, `getReadAccessCount`, `setReadAccessCount`.

## Control Flow
Mutable bean with simple Jackson property mapping.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should assert counts and read-access count population in namespace/heatmap endpoints.
