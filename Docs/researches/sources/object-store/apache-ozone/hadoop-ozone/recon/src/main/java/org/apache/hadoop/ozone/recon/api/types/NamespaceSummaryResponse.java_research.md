# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/NamespaceSummaryResponse.java

## Purpose
Response for namespace summary lookups, combining path, entity type, count stats, object metadata, and response status.

## Important APIs, Types, And Functions
declares `NamespaceSummaryResponse`, `Builder`; key fields include `path`, `entityType`, `countStats`, `objectDBInfo`, `status`, `path`, `entityType`, `countStats`, `objectDBInfo`, `status`; important methods include `newBuilder`, `getPath`, `getCountStats`, `getEntityType`, `getStatus`, `getObjectDBInfo`, `build`.

## Control Flow
Builder defaults status OK, path empty, and entity type UNKNOWN, then requires non-null path/entityType/status on build.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover required fields, invalid path status, and object metadata presence by entity type.
