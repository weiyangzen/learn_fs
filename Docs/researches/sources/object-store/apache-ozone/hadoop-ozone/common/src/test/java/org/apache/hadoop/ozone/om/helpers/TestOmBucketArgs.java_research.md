# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmBucketArgs.java

Purpose: tests `OmBucketArgs` protobuf conversion for quota-presence flags and default replication configuration.

Important APIs/types/functions: covers `OmBucketArgs.newBuilder`, `setQuotaInNamespace`, `setQuotaInBytes`, `hasQuotaInBytes`, `hasQuotaInNamespace`, `setDefaultReplicationConfig`, `getProtobuf`, and `getFromProtobuf`.

Control flow and state: one path builds args without quota and confirms both presence flags stay false before and after protobuf conversion. Another path sets namespace and byte quota and verifies both flags survive. Replication tests confirm absent default replication remains null and EC default replication round-trips as type `EC`.

Dependencies and integration points: uses HDDS `DefaultReplicationConfig` and `ECReplicationConfig`. These args are used by OM bucket create/update request handling.

Risks and test signals: protects distinction between unset quota and quota value defaults, and catches loss of bucket default replication policy across the protobuf boundary.
