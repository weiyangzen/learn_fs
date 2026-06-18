# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineManagerMXBean.java

## Purpose
`PipelineManagerMXBean` is the JMX management interface for pipeline manager state counts.

## Important APIs, Types, And Functions
It declares `getPipelineInfo`, returning a map from pipeline state name to count and allowing `NotLeaderException`.

## Control Flow
There is no implementation control flow. `PipelineManagerImpl.getPipelineInfo` supplies counts by iterating current pipelines.

## State And Persistence Behavior
The interface owns no state.

## Dependencies And Integration Points
It depends on Hadoop interface-audience annotations and Ratis `NotLeaderException`. Pipeline manager implementations expose it via MBeans.

## Risks And Edge Cases
The JMX contract exposes a leadership exception even though reads may be possible on followers depending on implementation. Consumers should handle missing/unavailable data.

## Test Signals
Implementation tests should verify all pipeline states are represented, zero counts are included, and leadership-related exceptions are handled by JMX callers.
