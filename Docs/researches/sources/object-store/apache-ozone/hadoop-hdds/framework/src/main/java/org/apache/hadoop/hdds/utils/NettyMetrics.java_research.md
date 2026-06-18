# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/NettyMetrics.java

## Purpose
`NettyMetrics` is a Hadoop metrics source that exports Netty direct-memory usage for HDDS services using Ratis-shaded Netty internals.

## Important APIs and Types
`create()` registers a `NettyMetrics` instance under `NettyMetrics.SOURCE_NAME` with `DefaultMetricsSystem`. `getMetrics` emits gauges for `USED_DIRECT_MEM` and `MAX_DIRECT_MEM`. `unregister()` removes the source.

## Control Flow and State
The class is stateless. On metrics collection, it reads `PlatformDependent.usedDirectMemory()` and `maxDirectMemory()` and writes them into one metrics record with context `Netty metrics`.

## Persistence, Dependencies, and Integration
No persistence exists. It depends on Hadoop Metrics2 and Ratis third-party Netty internals. It integrates with daemon metrics initialization where Netty memory pressure needs visibility.

## Risks and Test Signals
Metric values depend on Netty's direct-memory accounting being enabled and meaningful for the runtime. Duplicate registration can fail through the metrics system. Tests should cover registration/unregistration, metric names/descriptions, and behavior when Netty reports unavailable or sentinel values.
