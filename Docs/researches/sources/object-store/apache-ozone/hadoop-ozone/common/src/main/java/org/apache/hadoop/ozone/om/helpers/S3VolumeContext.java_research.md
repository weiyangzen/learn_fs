<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/S3VolumeContext.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/S3VolumeContext.java

## Purpose

`S3VolumeContext` wraps the S3 volume's `OmVolumeArgs` plus the user principal piggybacked for client-side KMS operations.

## Important APIs, Types, And Functions

The class exposes getters, static `fromProtobuf`, `getProtobuf`, `newBuilder`, and a nested builder with setters for `OmVolumeArgs` and user principal.

## Control Flow, State, And Persistence

It is a transient response wrapper for `GetS3VolumeContextResponse`. `getProtobuf` serializes volume info through `OmVolumeArgs.getProtobuf` and includes the principal. It does not persist independently.

## Dependencies And Integration Points

It depends on `OmVolumeArgs` and `GetS3VolumeContextResponse`. It integrates with S3 gateway key lookup, encryption/KMS paths, and `OzoneManagerProtocol.getS3VolumeContext`.

## Risks And Test Signals

The builder does not validate null fields. Tests should cover protobuf round trips, principal propagation for encrypted S3 keys, missing volume info, and compatibility with volume ACL/quota metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/S3VolumeContext.java -->
