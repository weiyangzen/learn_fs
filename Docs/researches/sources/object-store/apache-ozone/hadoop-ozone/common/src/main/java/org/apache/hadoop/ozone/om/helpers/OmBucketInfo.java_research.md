# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmBucketInfo.java

Purpose: Persisted bucket metadata model for OM DB and bucket RPC responses.

Important APIs/types/functions: Extends `WithObjectID`, implements `Auditable` and `CopyObject`. `CODEC` persists `BucketInfo` protobuf. Fields include volume/bucket, ACLs, versioning, storage type, creation/modification times, encryption, default replication, link source, used bytes/namespace, quotas, snapshot usage, bucket layout, owner, tags, metadata, object/update IDs. Builder supports copying and mutation. `getProtobuf` and `builderFromProtobuf` handle serialization.

Control flow and state: Usage counters are mutable. `incrUsedBytes`, `decrUsedBytes`, `incrUsedNamespace`, and `decrUsedNamespace` update live usage and optionally snapshot usage for pending deletes. `purgeSnapshotUsed*` reduces snapshot counters after cleanup. `isLink` is true when source volume and bucket are set.

State and persistence behavior: This is the authoritative bucket table value. Protobuf stores ACLs, metadata, tags, quotas, layout, usage, snapshot usage, object IDs, encryption, and link targets. `copyObject` uses the builder to produce a new metadata object.

Dependencies and integration points: Used by OM bucket table, quota accounting, snapshot accounting, S3 tagging, bucket links, audit logs, and replication defaults. Depends on `OzoneAclUtil`, `KeyValueUtil`, `BucketLayout`, `DefaultReplicationConfig`, `OMPBHelper`, and HDDS codecs.

Risks: Mutable usage fields mean shared references can observe accounting changes. Builder validation requires storage type and names but not semantic quota limits. Protobuf deserialization sets layout from either an override or proto; callers must pass overrides carefully during upgrades.

Test signals: Codec/protobuf round trips, quota and usage accounting including snapshot usage, bucket link serialization, layout defaults/upgrades, ACL/tag/metadata persistence, copy-object isolation, and audit map contents.
