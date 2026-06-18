<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/BucketObjectDBInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/BucketObjectDBInfo.java

## Purpose

`BucketObjectDBInfo` is the Recon API DTO for detailed bucket metadata read from OM DB.

## Important APIs and Types

It extends `ObjectDBInfo` and adds volume name, storage type, versioning flag, used bytes, snapshot used bytes, encryption info, default replication config, source volume/bucket, bucket layout, and owner. The `OmBucketInfo` constructor populates inherited metadata, quotas, namespace usage, timestamps, ACLs, and bucket-specific fields.

## Control Flow

The no-arg constructor supports serialization frameworks. The `OmBucketInfo` constructor performs a direct field mapping, including `AclMetadata.fromOzoneAcls`. Getters and setters expose all added fields except snapshot used bytes has only a getter in this file.

## State and Persistence

The object is a response DTO and does not persist data. Source persistence is OM bucket metadata.

## Dependencies and Integration Points

It is returned by `BucketEntityHandler` inside `NamespaceSummaryResponse` and depends on OM helper types such as `BucketEncryptionKeyInfo`, `BucketLayout`, `StorageType`, and `DefaultReplicationConfig`.

## Risks and Edge Cases

If `OmBucketInfo.getAcls()` is null, ACL conversion will throw. The DTO exposes encryption and replication helper objects directly, so JSON shape depends on those classes. Snapshot used bytes lacks a setter, which may matter for deserialization tests.

## Test Signals

Tests should verify full field mapping from `OmBucketInfo`, ACL serialization, linked bucket source fields, encryption and replication JSON shape, layout and owner fields, and null optional metadata behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/BucketObjectDBInfo.java -->
