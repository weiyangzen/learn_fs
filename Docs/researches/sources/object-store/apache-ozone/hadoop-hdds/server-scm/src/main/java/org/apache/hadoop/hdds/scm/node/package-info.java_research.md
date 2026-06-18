# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/package-info.java

## Purpose
This package descriptor documents the SCM node-management package: registration, removal, heartbeat handling, node statistics, and container-manager queries of datanode state.

## Important APIs, Types, And Functions
There are no executable APIs. The text describes the package role around node manager responsibilities and statistics exchanged through heartbeats.

## Control Flow
Not applicable. It is Java package documentation only.

## State And Persistence Behavior
No state is defined. It frames the state owned by package classes such as `SCMNodeManager`, `NodeStateManager`, and related state maps.

## Dependencies And Integration Points
The package integrates SCM datanode management with container manager and heartbeat/report processing components.

## Risks And Edge Cases
Documentation can drift as node manager responsibilities change, especially around admin state, HA leadership, and layout finalization, which are now significant parts of the package behavior.

## Test Signals
No direct tests are needed. Documentation should be reviewed when node management workflows are changed.
