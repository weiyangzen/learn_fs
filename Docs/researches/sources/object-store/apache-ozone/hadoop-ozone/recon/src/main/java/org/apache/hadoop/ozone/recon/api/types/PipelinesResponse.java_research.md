# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/PipelinesResponse.java

## Purpose
Response envelope for pipeline list APIs with total count and pipeline metadata rows.

## Important APIs, Types, And Functions
declares `PipelinesResponse`; key fields include `totalCount`, `pipelines`; important methods include `getTotalCount`, `getPipelines`.

## Control Flow
Default constructor initializes zero count and an empty list; alternate constructor accepts endpoint-produced values.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should assert empty output, count consistency, and pipeline row serialization.
