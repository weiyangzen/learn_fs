# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DUResponse.java

## Purpose
Disk usage response for namespace DU requests, including aggregate size, replicated size, direct key size, subpath count, and per-subpath usage rows.

## Important APIs, Types, And Functions
declares `DUResponse`, `DiskUsage`; key fields include `status`, `path`, `size`, `sizeWithReplica`, `count`, `duData`, `keySize`, `subpath`, `size`, `sizeWithReplica`; important methods include `getStatus`, `getSize`, `getSizeWithReplica`, `getPath`, `getCount`, `getKeySize`, `getDuData`, `getSize`, `getSubpath`, `getSizeWithReplica`, `isKey`.

## Control Flow
Defaults status to OK, initializes subpaths, and uses -1 sentinels when replica/direct-key accounting is disabled or unavailable.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover status changes, replicated-size sentinel values, `DiskUsage.isKey`, and empty subpath responses.
