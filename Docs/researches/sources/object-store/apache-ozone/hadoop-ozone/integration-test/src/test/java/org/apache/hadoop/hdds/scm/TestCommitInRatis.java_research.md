# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestCommitInRatis.java

## Purpose

`TestCommitInRatis` validates retry handling for Ozone output-stream flush/commit behavior when Ratis watch levels are `MAJORITY_COMMITTED` or `ALL_COMMITTED`. It focuses on correct propagation and recovery from retry failures in the write pipeline.

## Important APIs, Types, And Functions

The class configures chunk, flush, max-flush, and block sizes, starts a MiniOzoneCluster, and uses Ozone client APIs to create volumes, buckets, and keys. The parameterized test uses `RaftProtos.ReplicationLevel` values and exercises write/flush paths through Ratis.

## Control Flow

`startCluster` applies test configuration and creates the cluster/client. The parameterized test writes key data using a configured watch type, triggers flush/commit behavior, validates the expected retry path, and shuts the cluster down in cleanup logic.

## State And Persistence Behavior

The test persists key data through OM metadata, SCM block allocation, datanode chunks, and Ratis log commits. The observed state is whether committed data survives and whether exceptions align with the requested Ratis commit level.

## Dependencies And Integration Points

It depends on MiniOzoneCluster, Ozone client streams, Ratis replication-level APIs, and SCM/datanode write pipelines.

## Risks And Test Signals

As a Ratis timing test, it can be sensitive to commit latency. Failures indicate watch-level mismatch, retry error handling regressions, or data visibility bugs around flush/commit boundaries.
