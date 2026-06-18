# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMNodeManagerMXBean.java

## Purpose

`TestSCMNodeManagerMXBean` verifies JMX exposure from SCM's node manager, including disk usage and node-count information. It protects monitoring consistency for datanode health and capacity views.

## Important APIs, Types, And Functions

The abstract non-HA class uses `StorageContainerManager`, platform `MBeanServer`, JMX `TabularData`/`CompositeData`, and node manager methods `getNodeInfo()` and `getNodeCount()`. Helpers convert node-count objects into maps and compare tabular data to expected maps.

## Control Flow

Setup captures SCM. `testDiskUsage` reads the node-manager MXBean disk-usage attribute and compares it to SCM node manager data. `testNodeCount` reads node-count JMX data and compares it with internal counts grouped by state/status.

## State And Persistence Behavior

The test observes node manager state populated from datanode registration and reports. It does not mutate persistent metadata.

## Dependencies And Integration Points

It integrates SCM node manager, datanode reporting, Java JMX, and non-HA test scaffolding.

## Risks And Test Signals

Failures show MXBean schema drift, key/name mismatches in tabular data, or divergence between internal and exposed node metrics. Report timing can affect disk-usage visibility.
