# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/TestS3SDK.java

## Purpose

This concrete AWS SDK integration-test class runs the shared `OzoneS3SDKTests` harness with Ratis datastream disabled. It represents the standard non-datastream S3 write path.

## Important APIs, types, and functions

The class extends `OzoneS3SDKTests` and overrides `createOzoneConfig()`. It uses `OzoneConfigKeys.HDDS_CONTAINER_RATIS_DATASTREAM_ENABLED` and `ScmConfigKeys.OZONE_SCM_PIPELINE_OWNER_CONTAINER_COUNT`.

## Control flow, state, and persistence

`createOzoneConfig()` calls the superclass configuration factory, disables container Ratis datastream, sets SCM pipeline owner container count to 1, and returns the modified configuration. Cluster creation and test execution are inherited from `OzoneS3SDKTests` and its nested SDK suites.

## Dependencies and integration points

The configuration feeds `MiniOzoneCluster` before `MultiS3GatewayService` and the SDK v1/v2 abstract suites run. It integrates S3 Gateway compatibility tests with the regular block-output path.

## Risks and test signals

This class is intentionally small; most behavior is inherited. A low pipeline owner container count may increase pipeline churn and expose allocation edge cases. Positive signals are all inherited AWS SDK v1/v2 tests passing while datastream is disabled.
