# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/TestDatanodeConfiguration.java

## Purpose
`TestDatanodeConfiguration` verifies configuration binding, validation, defaults, and derived calculations for datanode container-service settings. It covers delete thread counts, disk check timing, failed-volume tolerances, block-delete worker intervals, min-free-space soft/hard thresholds, Ratis log appender wait time, and gRPC socket backlog.

## Important APIs, Types, And Functions
- `OzoneConfiguration.getObject(DatanodeConfiguration.class)` and `setFromObject` drive config binding.
- Constants under test include container delete threads, periodic disk checks, failed volume tolerances, disk check min gap/timeout, block delete worker interval, min free-space bytes/percent/hard-percent, and gRPC backlog.
- `DatanodeConfiguration.getMinFreeSpace`, `getHardLimitMinFreeSpace`, and `getSoftBandMinFreeSpaceWidth` implement derived disk-space behavior.
- `ContainerTestUtils.newXceiverServerRatis(...).newRaftProperties()` checks Ratis appender wait config integration.

## Control Flow
Positive and negative tests populate an `OzoneConfiguration`, bind it to `DatanodeConfiguration`, and assert valid values survive while invalid zero/negative values fall back to defaults. Default-value tests unset test-module overrides, capture logs, and assert no invalid-ratio warnings. Free-space tests vary fixed byte thresholds and percentages over several capacities, including the case where hard-limit ratio exceeds soft/reporting ratio. Ratis tests set `DatanodeRatisServerConfig.logAppenderWaitTimeMin`, write it back, and assert resulting Raft properties. gRPC tests assert default, configured, and setter values.

## State And Persistence Behavior
There is no persistence, but the suite validates configuration state materialization and derived capacity calculations used later by volume reporting and write enforcement. The Ratis path checks generated in-memory `RaftProperties`.

## Dependencies And Integration Points
The test depends on HDDS/Ozone configuration annotations, `DatanodeRatisServerConfig`, `MockPipeline`, Ratis `RaftServerConfigKeys`, and `ContainerTestUtils`. It integrates datanode config values with disk-space policy and Xceiver/Ratis server configuration.

## Risks And Edge Cases
Covered risks include invalid config values silently breaking runtime behavior, negative disk check durations, invalid min-free-space ratios outside `[0,1]`, byte and percent thresholds interacting incorrectly, hard threshold exceeding soft threshold, and gRPC backlog not honoring config. The default test includes a non-ASCII stray character in a comment only; executable behavior is unaffected.

## Test Signals
Signals are direct assertions on bound values, default fallback values, derived byte calculations for multiple capacities, log absence for defaults, and Ratis property equality.
