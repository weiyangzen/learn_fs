# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAWithStoppedNodes.java

## Purpose
Standard OM HA integration tests for leader/follower outages and restarts. It validates write availability with one OM down, failure with quorum loss, multipart upload failover, OM restart catch-up through snapshot install, key deletion replication, retry proxy behavior, list volumes after leader loss, HA metrics, and retry-cache continuity after leadership transfer.

## Important APIs, types, and functions
- Extends `TestOzoneManagerHA`.
- Uses `MiniOzoneHAClusterImpl`, `HadoopRpcOMFailoverProxyProvider`, `OMHAMetrics`, `KeyDeletingService`, `LogVerificationAppender`, and low-level `OzoneManagerProtocolProtos.OMRequest`.
- Uses Ratis `RaftClient.admin().transferLeadership` to force a new leader for retry-cache testing.
- Multipart helpers initiate MPU, create part keys, complete MPU with ETags, list parts, and read back data.

## Control flow
Each test starts after leader readiness and restarts OMs afterward. The suite stops one or two OMs and verifies operation success/failure. It stops the current proxy/leader to verify failover. Restart testing stops a follower, advances the leader far beyond purge gap, asserts the follower lags behind the leader snapshot, restarts it, waits for catch-up, then checks it applies later writes. Other tests validate list parts after leader stop, Ratis appender wait config, deleted table cleanup on all OMs, wait-time increments for same-node failover, HA leader-state metrics before/after leader restart, retry exhaustion logs, list-volume results after leader stop, and retry-cache reuse on a new leader after old leader shutdown.

## State and persistence behavior
The tests create and replicate volumes, buckets, keys, multipart upload parts, deleted-table entries, retry cache entries, Ratis logs, and snapshots. Key deletion state must be drained by `KeyDeletingService` and reflected in every OM's metadata table. Restart catch-up depends on snapshot installation when purged logs are unavailable.

## Dependencies and integration points
It spans HA cluster lifecycle, OM Ratis log/snapshot internals, client retry/failover state, multipart upload metadata, key deleting background service, OM HA metrics, Hadoop IPC current-call context, and Ratis leadership transfer.

## Risks and edge cases
Several tests are timing-sensitive due to sleeps and background services. Exact log message counts can change with retry policy changes. Low-level retry-cache tests manually set `Server.getCurCall`, so RPC/Ratis plumbing changes can affect setup.

## Test signals
Signals include operation success booleans, changed proxy/leader node ids, follower last-applied index catching up to snapshot index, part ETag equality, empty deleted tables on all OMs, HA leader-state metric values, retry log counts, expected `KEY_NOT_FOUND` after rename, and duplicate request success from retry cache on the new leader.
