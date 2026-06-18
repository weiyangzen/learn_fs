
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/S3StorageType.java

Purpose: maps S3 storage class names to Ozone `ReplicationConfig` values. `REDUCED_REDUNDANCY` maps to RATIS/ONE, `STANDARD` to RATIS/THREE, and `STANDARD_IA` to EC 3-2. The reverse helper `fromReplicationConfig` classifies EC as `STANDARD_IA`, standalone or one-node configs as reduced redundancy, and other configs as standard.

Important APIs and control flow: enum constants carry immutable replication config instances exposed by `getReplicationConfig()`. `fromReplicationConfig` depends on `getReplicationType()` and `getRequiredNodes()`, so it treats all EC configs the same regardless of actual EC layout.

State, dependencies, integration: no persistence beyond enum-held config objects. Used by `S3Utils.toReplicationConfig` and likely object PUT/listing code to translate `x-amz-storage-class`. Depends on HDDS replication classes and protobuf replication type/factor enums.

Risks and test signals: unsupported or future S3 storage classes are absent by design. Reverse mapping loses precision for custom EC layouts and any multi-node non-EC config is reported as `STANDARD`. Tests in this subset exercise storage-class headers indirectly in multipart endpoint setup but do not directly assert all enum mappings.
