# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestAllocateContainer.java

## Purpose

`TestAllocateContainer` exercises SCM's client-side container allocation API in a non-HA MiniOzoneCluster. It checks basic allocation, invalid replication input, and both RATIS and EC replication configurations.

## Important APIs, Types, And Functions

The abstract class implements `NonHATests.TestCase`, using `cluster()` from the injected non-HA fixture. `init()` creates a `StorageContainerLocationProtocolClientSideTranslatorPB`; `cleanup()` closes it. Tests call `allocateContainer`, `getContainer`, and `getContainerWithPipeline` using `RatisReplicationConfig`, `ECReplicationConfig`, and null replication.

## Control Flow

Setup creates the RPC translator from the cluster configuration. Each allocation test calls SCM, receives a container ID and pipeline, then validates that lookup by ID returns consistent metadata. The null replication test asserts that SCM rejects invalid input.

## State And Persistence Behavior

Allocations persist container metadata in SCM's container state manager and may create or select pipelines. The test does not write data blocks; it validates the control-plane state created by allocation.

## Dependencies And Integration Points

Dependencies include `StorageContainerLocationProtocolClientSideTranslatorPB`, replication config classes, `ContainerWithPipeline`, and `NonHATests`. It integrates with SCM's client protocol server and container manager.

## Risks And Test Signals

Failures indicate allocation API regressions, replication config validation gaps, EC/RATIS pipeline selection issues, or lookup inconsistency between allocation and container retrieval.
