# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshot.java

Purpose: `OmSnapshot` implements `IOmMetadataReader` for one OM snapshot. It wraps a snapshot-backed `KeyManager` and `PrefixManager` with an `OmMetadataReader`, normalizing user-facing `.snapshot/<name>/...` paths into snapshot DB keys and denormalizing results back to snapshot-prefixed paths.

Important APIs and types: read APIs mirror `IOmMetadataReader`: key lookup, get key info, list status, file status, lookup file, list keys, lightweight list, ACL read, and object tagging. Snapshot identity APIs expose `getName()`, `getSnapshotID()`, `getMetadataManager()`, `getKeyManager()`, and `getSnapshotTableKey()`.

Control flow: requests pass through `normalizeOmKeyArgs`, `normalizeKeyName`, or `normalizeOzoneObj` before delegation. Results use `denormalizeOmKeyInfo`, `denormalizeOzoneFileStatus`, or `denormalizeKeyInfoWithVolumeContext`. Bucket status responses with null `keyInfo` receive a synthetic zero-replication `OmKeyInfo` to carry the snapshot-prefixed key name.

State and persistence: holds snapshot identity and references a snapshot checkpoint `OMMetadataManager`. `close()` closes the snapshot DB store; `finalize()` logs a warning if the DB handle was not closed.

Dependencies and integration points: created by snapshot management code to serve snapshot read requests. It integrates with `OzoneAuthorizerFactory.forSnapshot`, `OmSnapshotManager` path helpers, `SnapshotInfo`, snapshot metrics, and key metadata classes.

Risks: path normalization must preserve trailing slashes and only strip valid snapshot prefixes. `listKeysLight` ignores its passed volume/bucket and uses the instance bucket, which is intentional for snapshots but should be covered. `finalize()` is a last-resort warning, not resource management.

Test signals: cover `.snapshot/name` root normalization, nested key normalization with trailing slash, denormalized lookup/list/file-status results, bucket status synthetic key info, close behavior, ACL normalization, and snapshot table key construction.
