# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMMXBean.java

## Purpose

`TestSCMMXBean` validates SCM JMX/MXBean exposure for SCM status and container state counts in a non-HA cluster. It ensures monitoring data matches SCM internal state.

## Important APIs, Types, And Functions

The abstract class implements `NonHATests.TestCase`. It queries platform `MBeanServer` object names, `StorageContainerManager`, SCM container manager, and JMX `TabularData`. Tests are `testSCMMXBean` and `testSCMContainerStateCount`; helper `verifyEquals` compares tabular rows to expected maps.

## Control Flow

Setup stores SCM from the cluster. Tests retrieve JMX attributes, compare SCM ID/cluster ID/service state fields, then compare container state counts from the MXBean against container manager values.

## State And Persistence Behavior

No new persistent state is the target. Container counts reflect SCM's in-memory and persisted container metadata. JMX exposes monitoring snapshots.

## Dependencies And Integration Points

It integrates SCM server state, Java Management Extensions, container manager state-count aggregation, and non-HA test fixtures.

## Risks And Test Signals

Failures indicate monitoring drift, broken MXBean registration/object names, or inconsistent container count aggregation. These are operational observability regressions rather than client data-path failures.
