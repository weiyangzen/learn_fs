# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/RemoveDataNodesResponseWrapper.java

## Purpose
Wrapper mapping remove-datanode request categories or IDs to `DatanodesResponse` objects.

## Important APIs, Types, And Functions
declares `RemoveDataNodesResponseWrapper`; key fields include `datanodesResponseMap`; important methods include `getDatanodesResponseMap`, `setDatanodesResponseMap`.

## Control Flow
Initializes an empty map and exposes it with XML/Jackson-friendly accessors, omitting empty values from JSON.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson inclusion, JAXB/XML. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover multiple response groups and empty-map omission.
