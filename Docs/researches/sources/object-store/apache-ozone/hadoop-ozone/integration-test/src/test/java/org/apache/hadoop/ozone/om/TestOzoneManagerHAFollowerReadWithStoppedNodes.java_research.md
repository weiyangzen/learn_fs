# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAFollowerReadWithStoppedNodes.java

## Purpose
Follower-read HA integration tests for stopped/restarted OM nodes. It verifies that leader and follower-read proxy providers fail over correctly when selected OMs go down, and that reads fail with expected Ratis/connectivity errors when quorum is lost.

## Important APIs, types, and functions
- Extends `TestOzoneManagerHAFollowerRead`.
- Uses `MiniOzoneHAClusterImpl`, `HadoopRpcOMFailoverProxyProvider`, `HadoopRpcOMFollowerReadFailoverProxyProvider`, and `OMProxyInfo`.
- Exercises volume/key creation, multipart upload create/complete/read, list volumes, and retry proxy logging.
- Helpers `changeFollowerReadInitialProxy(int/String)` force the follower-read provider to start from a target OM.

## Control flow
Before each test it waits for a ready leader; after each test it restarts all OMs. One-node-down tests stop a selected OM and expect writes/keys to succeed. Two-node-down tests expect writes to fail and follower reads to fail through `listVolumes(false)`. Multipart upload starts normally, then leader is stopped and the upload/read sequence must complete through failover. Separate tests verify leader proxy failover, follower-read proxy failover, skipping a stopped follower, incremental wait-time accounting, and max-failover retry logging when all OMs are stopped.

## State and persistence behavior
The suite creates replicated HA metadata for volumes, buckets, keys, and multipart upload state. Node stop/restart affects availability but should not lose committed metadata. Retry wait time and current proxy state are in-memory client/provider state.

## Dependencies and integration points
It integrates Ozone HA cluster lifecycle controls, client leader and follower-read failover providers, multipart upload metadata, Ratis leader election timing, log4j `LogVerificationAppender`, and node failure timeout constants.

## Risks and edge cases
Tests use sleeps based on `NODE_FAILURE_TIMEOUT` and client retry defaults, so they are timing-sensitive. The max-retry log assertions depend on exact log text. Follower-read behavior is sensitive to which node is the initial/current proxy.

## Test signals
Signals include operation success/failure booleans, changed proxy node ids after failover, follower-read provider still using follower reads, skipped stopped follower id, increased same-node wait time, and expected counts of failover log lines.
