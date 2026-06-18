# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/OpenKeyBytesInfo.java

## Purpose
Aggregate byte counters for open keys/files, multipart open keys, and their total.

## Important APIs, Types, And Functions
declares `OpenKeyBytesInfo`; key fields include `openKeyAndFileBytes`, `multipartOpenKeyBytes`, `totalOpenKeyBytes`; important methods include `getTotalOpenKeyBytes`, `getOpenKeyAndFileBytes`, `getMultipartOpenKeyBytes`.

## Control Flow
Constructor-only holder; producing services compute the sums from OM open-key and multipart tables.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify total equals component sums and large byte counts.
