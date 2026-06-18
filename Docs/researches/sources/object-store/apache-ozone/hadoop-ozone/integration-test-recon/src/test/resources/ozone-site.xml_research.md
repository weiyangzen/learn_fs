# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/resources/ozone-site.xml

## Purpose

This test resource supplies Ozone configuration defaults for Recon integration tests. It tunes OM, SCM, datanode, Ratis, heartbeat, snapshot-diff, container, and stream-buffer settings to make mini-cluster integration tests faster and more deterministic.

## Important settings

The file sets `ozone.om.transport.class` to `Hadoop3OmTransportFactory`, disables `ozone.om.s3.grpc.server_enabled`, raises OM and SCM handler counts to 20, enables Ratis datastream, shortens heartbeat intervals, limits SCM Ratis pipelines to 3, and sets close-container wait duration to 1 second. It also configures Ratis appender queue byte limits, chunk/block/container sizes, client stream buffer sizes, datastream packet/window sizes, and datanode minimum free space.

## Control flow, state, and persistence

The XML has no executable control flow. It is loaded into test configurations as a resource and changes runtime behavior of mini clusters created by the integration-test-recon module. Values persist only for the process-level configuration used by each test cluster.

## Dependencies and integration points

Settings affect Recon tests that rely on prompt heartbeat/report propagation, stream and datastream behavior, smaller block/container sizes, and predictable SCM/OM service responsiveness. The transport factory setting controls the OM client protocol implementation used in tests.

## Risks and test signals

Overly aggressive intervals can increase load or expose timing flakiness; larger handler counts can hide bottlenecks present in smaller deployments. Positive signals are faster cluster readiness, quick heartbeat-driven state convergence, and tests completing with bounded container/block sizes. Changes here can have broad effects across many Recon integration tests.
