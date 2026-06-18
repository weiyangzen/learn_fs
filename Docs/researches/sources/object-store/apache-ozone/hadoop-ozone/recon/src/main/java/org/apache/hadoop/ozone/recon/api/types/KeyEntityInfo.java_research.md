# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyEntityInfo.java

## Purpose
DTO for key or deleted-directory insight rows, including key/path, state age, logical and replicated size, replication config, creation/modification times, and `isKey` flag.

## Important APIs, Types, And Functions
declares `KeyEntityInfo`; key fields include `key`, `path`, `inStateSince`, `size`, `replicatedSize`, `replicationConfig`, `creationTime`, `modificationTime`, `isKey`; important methods include `getKey`, `getPath`, `getInStateSince`, `getSize`, `getReplicatedSize`, `getReplicationConfig`, `getCreationTime`, `getModificationTime`, `isKey`.

## Control Flow
Default construction sets times to current instant milliseconds and `isKey` true; setters allow insight services to override state and size fields.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, Jackson inclusion, HDDS replication. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover default time behavior, replicated size fields, and JSON omission for null replication config.
