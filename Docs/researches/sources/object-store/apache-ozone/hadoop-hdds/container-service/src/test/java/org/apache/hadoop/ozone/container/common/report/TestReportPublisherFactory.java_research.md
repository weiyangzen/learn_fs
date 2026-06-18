# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/report/TestReportPublisherFactory.java

## Purpose
`TestReportPublisherFactory` verifies that `ReportPublisherFactory` maps known heartbeat report protobuf classes to the correct publisher implementations and rejects unsupported classes.

## Important APIs, Types, And Functions
- `ReportPublisherFactory.getPublisherFor(Class<?>)` is the method under test.
- Known mappings checked are `ContainerReportsProto` to `ContainerReportPublisher` and `NodeReportProto` to `NodeReportPublisher`.
- Unsupported `HddsProtos.DatanodeDetailsProto` should throw a `RuntimeException`.

## Control Flow
Each positive test creates an `OzoneConfiguration`, asks the factory for a publisher by report class, and asserts the concrete class and retained configuration. The negative test requests a publisher for an unrelated protobuf class and asserts the exception message contains the expected diagnostic.

## State And Persistence Behavior
There is no persistence. The only state is the factory's mapping and each publisher's configuration reference.

## Dependencies And Integration Points
The factory integrates report protobuf types with scheduled publisher classes used by datanode heartbeats. The test depends on AssertJ/JUnit and HDDS protobuf classes.

## Risks And Edge Cases
The main risk is broken or stale class-to-publisher mapping, especially when new report types are added. Unsupported class handling is also covered.

## Test Signals
The test gives direct class equality, config equality, and exception-message signals.
