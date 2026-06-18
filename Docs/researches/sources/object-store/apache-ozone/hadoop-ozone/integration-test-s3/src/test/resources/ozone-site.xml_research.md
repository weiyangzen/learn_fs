# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/resources/ozone-site.xml

## Purpose

This `ozone-site.xml` is the test-resource configuration overlay for the `integration-test-s3` module. It tunes MiniOzoneCluster/S3 Gateway integration tests toward deterministic, faster behavior and S3-relevant data-path settings.

## Important Properties

- `ozone.om.transport.class` selects `org.apache.hadoop.ozone.om.protocolPB.Hadoop3OmTransportFactory`.
- `ozone.om.s3.grpc.server_enabled=false` disables the OM S3 gRPC server path for these tests, keeping coverage on the HTTP S3 Gateway path.
- Handler/thread settings such as `hdds.container.ratis.num.write.chunk.threads.per.volume=4`, `ozone.scm.handler.count.key=20`, and `ozone.om.handler.count.key=20` raise concurrency for test workloads.
- `hdds.container.ratis.datastream.enabled=true` enables datastream behavior in the container Ratis path.
- Heartbeat and close-container timing are shortened with `hdds.heartbeat.interval=1s`, `ozone.scm.heartbeat.thread.interval=100ms`, and `ozone.scm.close.container.wait.duration=1s`.
- Ratis queue byte limits are set for container, OM, and SCM HA appenders.
- Chunk/block/container and client buffer sizes are set to small test-friendly values: 1 MB chunks, 4 MB blocks, 128 MB containers, and MB-scale stream/datastream buffers.
- `hdds.datanode.volume.min.free.space=5GB` enforces a minimum free-space threshold in test datanodes.

## Control Flow and State Behavior

The file has no executable control flow. Hadoop/Ozone configuration loading treats each `<property>` entry as an override available on the test classpath. Those values affect cluster startup and runtime behavior before S3 tests issue operations.

The state impact is indirect but significant: smaller chunk/block sizes make multipart and allocation tests easier to reason about, short heartbeat intervals reduce waiting in cluster-state transitions, and disabling OM S3 gRPC avoids ambiguity about which S3 implementation path a test exercised.

## Dependencies and Integration Points

The file is consumed by Hadoop `Configuration` resource loading and MiniOzoneCluster test setup. It integrates with Ozone Manager, SCM, Ratis datastream, datanode volume checks, and S3 Gateway test modules.

## Risks and Edge Cases

- Timing reductions speed tests but can mask production timing behavior or introduce flakiness on slow hosts.
- The explicit free-space requirement can fail tests on constrained CI disks.
- Disabling OM S3 gRPC is intentional for this module; tests here should not be interpreted as covering that alternate server path.
- Small block/chunk sizes are useful for test coverage but may alter allocation patterns compared with production defaults.

## Test Signals

The configuration supports test signals in the SDK test bases: predictable block allocation for empty objects, faster snapshot/container/heartbeat convergence, multipart behavior with MB-scale parts, and consistent S3 Gateway routing.
