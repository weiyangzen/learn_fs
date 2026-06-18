# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/TestS3SDKWithRatisStreaming.java

## Purpose

This concrete AWS SDK integration-test class runs the shared S3 SDK compatibility suite with Ratis datastream enabled and configured as the default write path. It validates SDK behavior over Ozone's streaming write stack.

## Important APIs, types, and functions

The class extends `OzoneS3SDKTests` and overrides `createOzoneConfig()`. It sets `ScmConfigKeys.OZONE_SCM_PIPELINE_AUTO_CREATE_FACTOR_ONE`, `OzoneConfigKeys.HDDS_CONTAINER_RATIS_DATASTREAM_ENABLED`, `OzoneConfigKeys.OZONE_FS_DATASTREAM_ENABLED`, and `OzoneConfigKeys.OZONE_FS_DATASTREAM_AUTO_THRESHOLD`.

## Control flow, state, and persistence

`createOzoneConfig()` starts from the superclass configuration, disables automatic factor-one pipeline creation, enables container Ratis datastream, enables filesystem datastream, and sets the auto threshold to `0MB` so all writes use datastream. Cluster and nested SDK test execution are inherited.

## Dependencies and integration points

The class integrates the same proxy-backed multi-S3G harness with the datastream-enabled client/server code path. It is important coverage for put-object, multipart, and presigned operations under streaming semantics.

## Risks and test signals

Forcing all writes through datastream can expose differences in buffering, multipart upload handling, and small-object behavior. Disabling factor-one auto-create changes pipeline availability assumptions. Positive signals are inherited AWS SDK v1/v2 tests passing with datastream enabled for all write sizes.
