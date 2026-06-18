# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeysResponse.java

## Purpose
Response envelope for detailed key metadata lists, exposing total count, key rows, and the last key cursor.

## Important APIs, Types, And Functions
declares `KeysResponse`; key fields include `totalCount`, `keys`, `lastKey`; important methods include `getTotalCount`, `getKeys`, `getLastKey`.

## Control Flow
Constructor-only DTO; pagination semantics are supplied by the endpoint.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should assert last-key pagination and collection/count consistency.
