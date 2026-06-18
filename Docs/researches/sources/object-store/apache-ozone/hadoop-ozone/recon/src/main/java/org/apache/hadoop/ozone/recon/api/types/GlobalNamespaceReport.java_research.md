# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/GlobalNamespaceReport.java

## Purpose
Small immutable aggregate for namespace-level total used space and total key count.

## Important APIs, Types, And Functions
declares `GlobalNamespaceReport`; key fields include `totalUsedSpace`, `totalKeys`; important methods include `getTotalUsedSpace`, `getTotalKeys`.

## Control Flow
Values are constructor-provided and exposed via Jackson properties.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify aggregation service math and JSON property names.
