# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneSnapshotsNonHA.java

## Purpose
`TestOzoneSnapshotsNonHA` runs the shared `SnapshotTests` suite against a non-HA mini Ozone cluster. Its role is to prove the base snapshot behavior does not depend on OM HA.

## Important APIs, Types, and Functions
The class extends `SnapshotTests` and overrides only `createCluster()`, returning `newClusterBuilder().build()`. It uses JUnit per-class lifecycle through `@TestInstance`.

## Control Flow, State, and Persistence
All test flow lives in the inherited `SnapshotTests`; this subclass only changes cluster topology. Persistent state is whatever the inherited tests create in OM/SCM/DN mini-cluster metadata, but without HA Ratis peer behavior.

## Dependencies and Integration Points
The file integrates the generic snapshot test harness with the default `MiniOzoneCluster` builder. It acts as a topology adapter rather than a standalone test implementation.

## Risks and Test Signals
The main risk is that inherited tests may assume HA-specific timing or APIs despite this non-HA subclass. Signal comes from the base suite executing unchanged on a single-OM topology, catching accidental HA-only assumptions in snapshot logic.
