# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DeletionPendingBytesByComponent.java

## Purpose
Aggregate response for bytes pending deletion, with total bytes and a nested component-to-breakdown map.

## Important APIs, Types, And Functions
declares `DeletionPendingBytesByComponent`; key fields include `total`, `byComponent`; important methods include `getTotal`, `getByComponent`.

## Control Flow
Immutable constructor-only holder; map structure is supplied by the caller and exposed directly.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify nested map JSON shape and that total matches component sums in producing services.
