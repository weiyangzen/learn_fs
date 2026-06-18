# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestContainerOperations.java

## Purpose

`TestContainerOperations` covers SCM container CLI/client operations in a non-HA cluster: create/list/get pipeline, idempotent state transitions, datanode usage compatibility, healthy-node counts, operational states, and RATIS/EC create paths.

## Important APIs, Types, And Functions

The abstract class implements `NonHATests.TestCase`. Setup creates `ContainerOperationClient` and `ScmClient`. Tests use `ContainerWithPipeline`, `DatanodeUsageInfo`, `NodeStatus`, `RatisReplicationConfig`, `ECReplicationConfig`, and SCM container lifecycle APIs.

## Control Flow

The test fixture obtains SCM clients, then individual tests allocate/create containers, list with a limit, fetch pipeline details, inspect datanode usage, query node counts, and change node operational states such as `IN_SERVICE`, `DECOMMISSIONING`, and `IN_MAINTENANCE`. Replication-specific create helpers validate returned pipelines.

## State And Persistence Behavior

Container creation persists container records in SCM metadata and may create pipelines. Node operational-state changes update SCM node manager state. Usage info reflects datanode reports and compatibility fields.

## Dependencies And Integration Points

It integrates SCM client protocol, container manager, node manager, datanode usage reporting, and replication config handling. It is a bridge between CLI/client surface and SCM internal state.

## Risks And Test Signals

Failures reveal API/CLI contract drift, bad container-list limits, pipeline lookup inconsistency, broken node usage compatibility, or operational-state accounting regressions. Asynchronous reports can make usage-related assertions timing-sensitive.
