# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/UnhealthyContainersSummary.java

## Purpose
Small summary row pairing an unhealthy container state string with its count.

## Important APIs, Types, And Functions
declares `UnhealthyContainersSummary`; key fields include `count`, `containerState`; important methods include `getContainerState`, `getCount`.

## Control Flow
Constructor-only immutable holder.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify state labels and counts from summary queries.
