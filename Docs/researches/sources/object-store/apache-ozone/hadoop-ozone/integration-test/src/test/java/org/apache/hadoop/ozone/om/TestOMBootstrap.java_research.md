# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMBootstrap.java

## Purpose
`TestOMBootstrap` verifies that a stopped OM follower can bootstrap from an installed checkpoint after the leader has advanced, for both v1 and v2 OM DB checkpoint formats. It ensures metadata and snapshots are restored on the follower.

## Important APIs, Types, and Functions
- The class is parameterized over `useV2Checkpoint`.
- `init()` configures checkpoint format, small Ratis purge gap and segment sizes, snapshot auto-trigger threshold, log appender wait time, client RPC timeout, and a three-OM HA cluster with an object-store test bucket.
- `testBootstrapFollower()` stops a follower, writes keys and snapshots on the leader, restarts the follower, waits for catch-up, asserts checkpoint-install log messages and endpoint selection, verifies metadata tables, and checks snapshot contents.
- `assertLogCapture(...)` waits until captured logs contain a message.

## Control Flow
The test determines the leader via `OmTestUtil.getCurrentOmProxyNodeId`, selects a follower from leader peer nodes, stops it, writes 25 keys and snapshot `snap1`, writes five more keys and snapshot `snap2`, captures OM and snapshot-provider logs, restarts the follower, computes leader transaction term/index from metadata, waits until follower last-applied index reaches the leader snapshot index, and then validates logs, metadata rows, RPC server restart, and snapshot equivalence.

## State and Persistence Behavior
State under test includes OM Ratis log/snapshot state, DB checkpoints served over v1 or v2 HTTP endpoints, volume/bucket/key metadata, snapshot metadata, and follower OM local DB after checkpoint install. The follower must reload state and resume RPC service.

## Dependencies and Integration Points
Dependencies include MiniOzone HA cluster, OM Ratis snapshot helpers (`TestOMRatisSnapshots`), `OmRatisSnapshotProvider`, DB checkpoint endpoint constants, `TransactionInfo`, Ratis `TermIndex`, Ozone client/object store, and log capture utilities.

## Risks and Test Signals
Risks include timing around follower stop/restart, snapshot index comparison, and log-message coupling. Signals include captured `"Reloaded OM state"` and `"Install Checkpoint is finished"` messages, expected v1/v2 endpoint in snapshot-provider logs, follower metadata rows for all keys, follower RPC server running, and snapshot content checks matching leader state.
