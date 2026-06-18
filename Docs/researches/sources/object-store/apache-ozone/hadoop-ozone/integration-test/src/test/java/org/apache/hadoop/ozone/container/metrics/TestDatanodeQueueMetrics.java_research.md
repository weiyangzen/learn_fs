# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/metrics/TestDatanodeQueueMetrics.java

Purpose: This abstract non-HA test verifies that datanode queue metrics expose non-negative gauges for every SCM command type in both the state-context command queue and command-dispatcher queue.

Important APIs and types: It uses `DatanodeQueueMetrics`, `SCMCommandProto.Type`, metric prefixes `STATE_CONTEXT_COMMAND_QUEUE_PREFIX` and `COMMAND_DISPATCHER_QUEUE_PREFIX`, Apache Commons Text `WordUtils.capitalize`, `MetricsAsserts.getMetrics`, `MetricsAsserts.getLongGauge`, AssertJ, and the `NonHATests.TestCase` fixture interface.

Control flow: `testQueueMetrics` iterates all generated `SCMCommandProto.Type` enum values. For each type it builds a metric suffix from the capitalized enum value plus `Size`, then fetches gauges for state-context and command-dispatcher queues and asserts both are greater than or equal to zero. The test relies on the surrounding non-HA fixture to have datanode metrics registered before execution.

State and persistence behavior: No durable state is involved. The state under test is the metrics system's current gauge values for command queues. The values may be zero or positive depending on queued commands, but must not be absent or negative.

Dependencies and integration points: It connects generated SCM command protobuf types to datanode queue metric naming. This is useful coverage when adding command types, because the loop expects a gauge for every enum value in both queue surfaces.

Risks: Metric names depend on exact capitalization of enum string values, so enum naming or metric naming changes require coordinated updates. The class is abstract and depends on an external concrete non-HA test harness; run in isolation it is not a complete cluster setup.

Test signals: The signal is simple but broad: for every SCM command type, both queue-size gauges are present and non-negative under `DatanodeQueueMetrics.METRICS_SOURCE_NAME`.
