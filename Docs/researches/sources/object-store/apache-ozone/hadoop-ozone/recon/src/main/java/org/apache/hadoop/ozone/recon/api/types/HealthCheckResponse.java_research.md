# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/HealthCheckResponse.java

## Purpose
Simple health response with message and numeric status for Recon health endpoints.

## Important APIs, Types, And Functions
declares `HealthCheckResponse`, `Builder`; key fields include `message`, `status`, `message`, `status`; important methods include `getMessage`, `getStatus`, `build`.

## Control Flow
Builder copies message/status into an immutable response with Jackson properties.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should assert status/message mapping from health resources.
