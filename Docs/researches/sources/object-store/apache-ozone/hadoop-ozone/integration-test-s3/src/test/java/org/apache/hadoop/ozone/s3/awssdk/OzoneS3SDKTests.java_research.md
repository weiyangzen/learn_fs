# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/OzoneS3SDKTests.java

## Purpose

This abstract test harness runs the shared AWS SDK S3 compatibility suites against a MiniOzoneCluster fronted by multiple S3 Gateways behind a proxy. It provides nested SDK v1 and SDK v2 test classes over the same cluster.

## Important APIs, types, and functions

The class extends `ClusterForTests<MiniOzoneCluster>`, overrides `createCluster()`, and defines nested classes `V1` and `V2`. `createCluster()` calls `newClusterBuilder().addService(new MultiS3GatewayService(5)).build()`. `V1` extends `AbstractS3SDKV1Tests`; `V2` extends `AbstractS3SDKV2Tests`; both implement `cluster()` by returning `getCluster()`.

## Control flow, state, and persistence

The inherited `ClusterForTests` lifecycle creates and tears down the mini cluster. The added `MultiS3GatewayService` starts five S3G instances and a proxy, mutating S3G endpoint configuration so SDK clients use the proxy. Nested JUnit suites run many inherited S3 operations against that cluster.

## Dependencies and integration points

This is the glue between Ozone mini-cluster lifecycle, the S3 proxy/gateway service, and the broad abstract AWS SDK v1/v2 test suites. Concrete subclasses adjust Ozone configuration for normal or Ratis streaming write modes.

## Risks and test signals

Any lifecycle bug in `MultiS3GatewayService` affects all nested SDK tests. Because both nested suites share one cluster, state cleanup in the abstract suites must be reliable. Positive signals are both SDK generations running against the same proxied multi-gateway endpoint and inherited tests passing under this cluster harness.
