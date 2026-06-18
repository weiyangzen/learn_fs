<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/OpenContainerHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/OpenContainerHandler.java

## Purpose

`OpenContainerHandler` handles open containers by closing those that have no healthy pipeline or whose replicas no longer match the open state. It stops further ReplicationManager processing for open containers.

## Important APIs, Types, and Functions

The main methods are `handle` and private `isOpenContainerHealthy`. It uses `ReplicationManager.hasHealthyPipeline`, `sendCloseContainerEvent`, `ReplicationManager.compareState`, and report states `OPEN_WITHOUT_PIPELINE` and `OPEN_UNHEALTHY`.

## Control Flow

Only `OPEN` containers are handled. The handler first checks for a healthy pipeline; if absent it closes without testing replica health. Otherwise it checks all replicas match the container state. Unhealthy open containers are sampled and, unless read-only, a close-container event is sent. All open containers return handled to stop the chain.

## State and Persistence Behavior

It owns no state. Side effects are report sampling and a close event that later drives lifecycle transition and datanode commands.

## Dependencies and Integration Points

It integrates with pipeline health, event-driven close handling, health reports, and the chain ordering that should keep open containers out of closed-container replication repair logic.

## Risks and Edge Cases

An empty replica set is considered healthy by `allMatch` if a pipeline exists, so no-pipeline is the primary empty-open protection. Read-only scans still classify but do not close.

## Test Signals

Tests should cover open-without-pipeline close event, open unhealthy replica close event, healthy open no event, read-only no event, non-open pass-through, and chain stop for any open container.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/OpenContainerHandler.java -->
