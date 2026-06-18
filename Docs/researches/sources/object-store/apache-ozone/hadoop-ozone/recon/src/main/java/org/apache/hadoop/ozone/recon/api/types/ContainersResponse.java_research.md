# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainersResponse.java

## Purpose
Response envelope for container list APIs. The external JSON root is `data`, containing total count, previous pagination key, and container rows.

## Important APIs, Types, And Functions
declares `ContainersResponse`, `ContainersResponseData`; key fields include `containersResponseData`, `totalCount`, `prevKey`, `containers`; important methods include `getContainersResponseData`, `setContainersResponseData`, `getTotalCount`, `getContainers`, `getPrevKey`.

## Control Flow
The default constructor creates zero count, empty container collection, and prevKey zero; non-default construction wraps values in `ContainersResponseData`.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should assert nested JSON shape and pagination `prevKey` semantics.
