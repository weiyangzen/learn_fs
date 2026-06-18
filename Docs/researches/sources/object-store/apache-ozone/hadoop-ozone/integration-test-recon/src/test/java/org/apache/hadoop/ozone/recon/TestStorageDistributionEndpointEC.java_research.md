# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestStorageDistributionEndpointEC.java

## Purpose

This subclass tests the Recon storage-distribution and pending-deletion endpoints under EC replication. It uses a five-datanode cluster to satisfy RS-3-2 placement and reuses shared setup and verification logic from `AbstractTestStorageDistributionEndpoint`.

## Important APIs, types, and functions

The class extends `AbstractTestStorageDistributionEndpoint`, overrides `getNumDatanodes()`, and provides `setup()` and `testStorageDistributionEndpoint()`. It uses `ECReplicationConfig(3, 2)`, `OzoneBucket`, Hadoop `FileSystem`, `Path`, and `GenericTestUtils.waitFor()`.

## Control flow, state, and persistence

The test initializes a five-datanode cluster, creates an FSO bucket with EC default replication, creates open and multipart keys through the base helper, then writes 20 finalized filesystem keys across `/dir1` and `/dir2`. It waits for storage distribution to show expected global namespace and storage data, closes all containers, deletes `/dir1`, and then waits for pending-deletion signals at OM, SCM, and DN components. It finally waits for SCM's deleted-block summary to clear and for DN pending deletion to clear.

## Dependencies and integration points

The test depends on the abstract base for cluster tuning, endpoint HTTP calls, JSON parsing, OM sync, pending-deletion checks, and container close events. It integrates EC replicated-size accounting with Recon's storage-distribution and pending-deletion APIs.

## Risks and test signals

The EC path needs enough datanodes and can be timing-sensitive around block deletion and datanode metric collection. Positive signals are the base verifier's expected namespace totals, per-datanode usage matching SCM reports, OM pending deletion of 300 bytes, SCM pending deletion of 10 blocks/100 unreplicated bytes/300 replicated bytes, DN pending deletion distributed across five nodes, and eventual DN pending-deletion clearance.
