# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestWatchForCommit.java

## Purpose

`TestWatchForCommit` validates Ozone output stream handling of Ratis watch-for-commit behavior. It covers normal key writes, retry failure, timeout, and group-mismatch cases for both majority and all-committed watch levels. The class is marked flaky for HDDS-5818.

## Important APIs, Types, And Functions

The test configures small chunk/flush/block sizes, MiniOzoneCluster, Ozone client volumes/buckets, and Ratis client settings. Parameterized tests use `RaftProtos.ReplicationLevel.MAJORITY_COMMITTED` and `ALL_COMMITTED`. Helpers include `createKey` and `validateData`.

## Control Flow

Setup starts a cluster and bucket. `testWatchForCommitWithKeyWrite` writes data and validates it can be read. Parameterized retry and timeout tests configure failure conditions around Ratis commit watching and assert expected exceptions/behavior. The group mismatch test simulates a commit watch against the wrong group and validates error handling. Cleanup shuts down client and cluster.

## State And Persistence Behavior

Successful paths persist OM key metadata, SCM block allocations, datanode chunks, and Ratis commit state. Failure paths exercise partial writes, retries, and exception handling without accepting corrupt committed data.

## Dependencies And Integration Points

It integrates Ozone output streams, SCM allocation, datanode Ratis pipelines, Ratis watch APIs, and client readback validation.

## Risks And Test Signals

Failures indicate incorrect commit-level semantics, lost data after successful writes, bad retry/timeout propagation, or unsafe handling of Ratis group mismatches. Timing and injected failure conditions make the suite sensitive.
