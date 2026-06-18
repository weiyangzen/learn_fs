# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestStorageDistributionEndpointRatis.java

## Purpose

This subclass tests the Recon storage-distribution and pending-deletion endpoints under RATIS THREE replication. It also verifies the DN pending-deletion endpoint's behavior when a datanode is stopped.

## Important APIs, types, and functions

The class extends `AbstractTestStorageDistributionEndpoint`, overrides `getNumDatanodes()`, and provides `setup()` and `testStorageDistributionEndpoint()`. It uses `RatisReplicationConfig.getInstance(THREE)`, `OzoneBucket`, Hadoop `FileSystem`, `Path`, and `GenericTestUtils.waitFor()`.

## Control flow, state, and persistence

The test initializes a three-datanode cluster, creates an FSO bucket with RATIS THREE replication, creates open and multipart keys, writes 20 filesystem keys under two directories, and waits for storage-distribution assertions. It closes all containers, deletes `/dir1`, waits for pending-deletion visibility at OM, SCM, and DN, waits for SCM deleted blocks to clear, waits for DN pending deletion to clear, then stops one datanode and verifies the DN endpoint records a query failure.

## Dependencies and integration points

Like the EC subclass, it relies on the abstract base for configuration, endpoint access, OM sync, and verification. The final stopped-datanode scenario integrates Recon's datanode metrics collection with partial failure reporting.

## Risks and test signals

Timing is sensitive around container close events, block deletion, DN metric collection, and the stopped-node query failure. Positive signals include the same storage and pending-deletion totals as the base verifier with three datanodes, DN pending deletion distributed as 100 bytes per node before cleanup, zero pending deletion after cleanup, and a DN metrics response with one query failure and a `-1` per-node pending block size.
