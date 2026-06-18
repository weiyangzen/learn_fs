# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestStorageContainerManagerHA.java

## Purpose

`TestStorageContainerManagerHA` validates SCM HA bootstrap behavior and leadership metrics in clusters with multiple OMs and SCMs. It covers primordial SCM startup, adding SCMs, and metrics that expose leadership state.

## Important APIs, Types, And Functions

The class uses MiniOzone HA builder APIs, `StorageContainerManager`, SCM bootstrap/deactivation utilities, and metrics assertions. Tests are `testPrimordialSCM`, `testBootStrapSCM`, and `testSCMLeadershipMetric`; setup initializes HA cluster parameters and teardown shuts the cluster down.

## Control Flow

Initialization builds a HA topology. The primordial test validates initial SCM HA state. The bootstrap test brings additional SCMs into the service and checks cluster readiness. The metrics test reads leadership metrics and confirms leader/follower reporting aligns with actual SCM roles.

## State And Persistence Behavior

The tests mutate SCM HA membership, SCM storage initialization, Ratis peer state, and metrics values. Bootstrap persists SCM identity and service membership.

## Dependencies And Integration Points

It integrates MiniOzone HA orchestration, SCM bootstrap flow, Ratis leadership, and metrics registration.

## Risks And Test Signals

Failures indicate bootstrap regressions, incorrect primordial SCM assumptions, role-reporting drift, or HA metrics not matching Ratis leadership. Cluster startup and leader election timing are key risks.
