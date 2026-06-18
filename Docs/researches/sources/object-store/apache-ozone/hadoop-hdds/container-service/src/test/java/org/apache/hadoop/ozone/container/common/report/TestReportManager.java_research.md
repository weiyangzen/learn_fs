# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/report/TestReportManager.java

## Purpose
`TestReportManager` checks that `ReportManager` initializes registered report publishers with the configured `StateContext` and an internal `ScheduledExecutorService`.

## Important APIs, Types, And Functions
- `ReportManager.newBuilder(conf)` creates the builder.
- `setStateContext`, `addPublisher`, `build`, and `init` define the tested setup path.
- `ReportPublisher.init(StateContext, ScheduledExecutorService)` is verified on a mock publisher.

## Control Flow
The test creates a dummy context and dummy publisher, adds the publisher to a builder, builds the manager, calls `init`, and verifies the publisher receives exactly one initialization call with the context and any scheduled executor.

## State And Persistence Behavior
There is no persistence. The state under test is the manager's publisher list and executor initialization.

## Dependencies And Integration Points
This test links report scheduling to `StateContext`, which later supplies heartbeat reports. It depends on Mockito and `OzoneConfiguration`.

## Risks And Edge Cases
The main risk covered is forgetting to initialize added publishers. It does not verify executor shutdown or multiple publishers, but the single-publisher check confirms the builder-to-init path.

## Test Signals
The signal is a Mockito verification of publisher initialization count and arguments.
