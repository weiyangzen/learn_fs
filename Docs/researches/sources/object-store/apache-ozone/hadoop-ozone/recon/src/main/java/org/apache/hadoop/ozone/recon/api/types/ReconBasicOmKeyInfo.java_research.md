# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ReconBasicOmKeyInfo.java

## Purpose
Lightweight immutable OM key representation optimized for Recon event handling and list-key responses without full key location/ACL payloads.

## Important APIs, Types, And Functions
declares `ReconBasicOmKeyInfo`, `Builder`; key fields include `volumeName`, `bucketName`, `keyName`, `dataSize`, `creationTime`, `modificationTime`, `key`, `path`, `replicatedSize`, `replicationConfig`; important methods include `getCodec`, `getVolumeName`, `getBucketName`, `getKeyName`, `getDataSize`, `getCreationTime`, `getModificationTime`, `getReplicationConfig`, `isFile`, `getReplicatedSize`, `getKey`, `getPath`.

## Control Flow
Provides a decode-only codec from `KeyInfoProtoLight`, protobuf conversion helpers from light and full key protos, replicated-size derivation through `QuotaUtil`, and JSON getters that require `key` and `path` to be set before serialization.

## State And Persistence Behavior
This type is persistence-adjacent: Recon stores or decodes it from OM/Recon metadata representations, so field compatibility and codec/protobuf behavior are part of the durable contract.

## Dependencies And Integration Points
Integrates with Jackson, HDDS replication, OM protobuf. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are serialization failures when `key` or `path` are not set, decode-only codec expectations, replicated-size changes when replication config semantics change, and equality/hashCode using different field sets.

## Test Signals
Tests should cover protobuf conversion, decode-only codec behavior, replicated size for replication configs, directory key naming, and serialization exceptions when key/path are missing.
