<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/AbstractCheck.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/AbstractCheck.java

## Purpose

`AbstractCheck` is the base class for ReplicationManager container health checks. It implements a simple chain-of-responsibility so each handler can either handle a container or pass it to the next handler.

## Important APIs, Types, and Functions

It implements `HealthCheck.handleChain` and `HealthCheck.addNext`, stores one successor `HealthCheck`, and leaves `handle(ContainerCheckRequest)` abstract for concrete checks.

## Control Flow

`handleChain` calls the current handler's `handle`. If it returns `false` and a successor exists, it invokes the successor's `handleChain`; otherwise it returns the current result. `addNext` replaces the successor and returns the added handler to support fluent chain construction.

## State and Persistence Behavior

State is an in-memory successor pointer. There is no persistence and no synchronization, so chains are expected to be built during initialization.

## Dependencies and Integration Points

Concrete handlers in the `health` package extend this class and receive `ContainerCheckRequest`, which carries container info, replicas, pending ops, reports, queue, and read-only mode.

## Risks and Edge Cases

Handler return values are semantically important: some handlers send commands but return `false` so later checks continue. Replacing the successor after startup could alter chain behavior without thread safety.

## Test Signals

Tests should verify pass-through on `false`, stop on `true`, fluent chaining order, and concrete handlers that intentionally return `false` after side effects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/AbstractCheck.java -->
