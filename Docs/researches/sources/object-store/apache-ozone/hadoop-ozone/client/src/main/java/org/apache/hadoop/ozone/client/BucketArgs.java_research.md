# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/BucketArgs.java

## Purpose
Immutable client-side argument object and builder used when creating or linking Ozone buckets, including ACLs, metadata, quotas, layout, owner, encryption, and default replication. This research is based on a complete read of the 286-line source file.

## Important APIs and Types
Types: `encapsulates`, `BucketArgs`, `that`, `Builder`. Important methods: `getVersioning`, `getStorageType`, `getAcls`, `getMetadata`, `getEncryptionKey`, `getDefaultReplicationConfig`, `newBuilder`, `getSourceVolume`, `getSourceBucket`, `getQuotaInBytes`, `getQuotaInNamespace`, `getBucketLayout`.

## Control Flow
Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Instances are immutable after `Builder.build()`: ACLs and metadata are copied into immutable collections, quota defaults use `OzoneConsts.QUOTA_RESET`, and all persistence happens later through client APIs that consume the object.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.client` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: HDDS config/replication helpers.

## Risks and Edge Cases
Builder accepts nullable fields and performs little validation; callers and server-side code must enforce semantic constraints.

## Test Signals
Builder immutability/defaults are unit-testable through getter assertions and mutation-after-build checks.
