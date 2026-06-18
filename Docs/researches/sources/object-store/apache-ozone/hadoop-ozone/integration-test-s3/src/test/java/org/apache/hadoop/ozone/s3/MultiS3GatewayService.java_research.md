# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/MultiS3GatewayService.java

## Purpose

This mini-cluster service starts multiple S3 Gateway instances and exposes them through one Jetty reverse proxy. It lets SDK integration tests exercise S3 behavior through a load-balanced gateway front door.

## Important APIs, types, and functions

The class implements `MiniOzoneCluster.Service`. It owns a list of `S3GatewayService` instances, a `ProxyServer`, and a constructor that accepts the number of gateways. `start()` launches each gateway, collects its HTTP endpoint, rewrites the cluster S3G HTTP address to the proxy address, and starts the proxy. `stop()` shuts down the proxy and all gateways while preserving/suppressing exceptions.

## Control flow, state, and persistence

At startup, each child gateway receives the same input `OzoneConfiguration` and internally binds to free ports. The service collects `http://host:port` URLs from each child gateway's held configuration. It then allocates a free proxy address, stores it in the passed configuration under `OZONE_S3G_HTTP_ADDRESS_KEY`, constructs `ProxyServer`, and starts it. Runtime state is in-memory Jetty/S3G processes only.

## Dependencies and integration points

The class integrates `S3GatewayService`, `ProxyServer`, `S3GatewayConfigKeys`, and `MiniOzoneCluster` service lifecycle. `OzoneS3SDKTests` adds `new MultiS3GatewayService(5)` to the test cluster, so all nested AWS SDK tests use the proxy-facing S3 endpoint.

## Risks and test signals

The `configuration` field is never assigned, so `getConf()` returns null; current callers appear to use the mutated cluster config instead, but direct callers would fail. Startup does not roll back already-started child gateways if a later gateway or proxy fails. Positive signals are the SDK tests reaching the proxy address from configuration, requests being distributed by the proxy, and `stop()` collecting failures without skipping remaining services.
