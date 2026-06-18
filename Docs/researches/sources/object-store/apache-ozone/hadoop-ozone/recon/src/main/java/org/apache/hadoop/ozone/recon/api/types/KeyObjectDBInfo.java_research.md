# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/KeyObjectDBInfo.java

## Purpose
Object DB representation of an OM key for Recon APIs, including volume, bucket, key name, size, location versions, replication, encryption, file flag, and file name.

## Important APIs, Types, And Functions
declares `KeyObjectDBInfo`; key fields include `volumeName`, `bucketName`, `keyName`, `dataSize`, `keyLocationVersions`, `replicationConfig`, `encInfo`, `isFile`, `fileName`; important methods include `getVolumeName`, `getBucketName`, `getKeyName`, `getDataSize`, `getKeyLocationVersions`, `getReplicationConfig`, `isFile`, `getFileName`, `getEncInfo`.

## Control Flow
The `OmKeyInfo` constructor copies only fields needed by Recon/UI from OM metadata; setters support tests and manual composition.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, HDDS replication. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover constructor mapping from `OmKeyInfo`, encrypted keys, directory-vs-file flags, and replication info.
