# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmBucketInfo.java

Purpose: validates `OmBucketInfo` equality, protobuf conversion, bucket-link metadata, cloning, ACL copying, and EC default replication serialization.

Important APIs/types/functions: exercises `OmBucketInfo.newBuilder`, `getProtobuf`, `getFromProtobuf`, `copyObject`, `setSourceVolume`, `setSourceBucket`, `setDefaultReplicationConfig`, `getDefaultReplicationConfig`, and ACL getters.

Control flow and state: tests construct normal and linked buckets, round-trip through protobuf, copy objects and compare equality/not-same identity, then verify ACL entries are retained. EC tests assert protobuf has no default replication when unset and has EC data/parity when set.

Dependencies and integration points: uses `StorageType`, `OzoneAcl`, `IAccessAuthorizer`, HDDS replication config classes, and OM protobuf `BucketInfo`.

Risks and test signals: catches shallow clone problems, lost bucket-link fields, lost ACLs, and mismatch between legacy replication fields and modern default replication config. Important for OM metadata persistence and bucket update semantics.
