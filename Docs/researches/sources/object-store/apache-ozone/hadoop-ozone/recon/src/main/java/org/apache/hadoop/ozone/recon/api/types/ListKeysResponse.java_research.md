# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ListKeysResponse.java

## Purpose
Namespace list-keys response used by Recon UI/chatbot: status, path, replicated and unreplicated totals, last key cursor, and basic key rows.

## Important APIs, Types, And Functions
declares `ListKeysResponse`; key fields include `status`, `path`, `replicatedDataSize`, `unReplicatedDataSize`, `lastKey`, `keys`; important methods include `getStatus`, `setStatus`, `getReplicatedDataSize`, `setReplicatedDataSize`, `getUnReplicatedDataSize`, `setUnReplicatedDataSize`, `getPath`, `setPath`, `getKeys`, `setKeys`, `getLastKey`, `setLastKey`.

## Control Flow
Defaults status OK and initializes an empty `ReconBasicOmKeyInfo` list; non-empty lists are included in JSON.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, Jackson inclusion. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover empty directories, pagination, error statuses, and aggregate size totals.
