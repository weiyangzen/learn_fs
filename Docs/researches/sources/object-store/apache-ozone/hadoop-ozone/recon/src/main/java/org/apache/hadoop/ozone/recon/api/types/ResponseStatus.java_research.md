# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ResponseStatus.java

## Purpose
Shared enum for Recon API response status values: OK, PATH_NOT_FOUND, and TYPE_NOT_APPLICABLE.

## Important APIs, Types, And Functions
declares `ResponseStatus`.

## Control Flow
Used by namespace, DU, quota, file-size, and key-list responses as a compact status discriminator.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should assert endpoint-specific mapping to these enum values.
