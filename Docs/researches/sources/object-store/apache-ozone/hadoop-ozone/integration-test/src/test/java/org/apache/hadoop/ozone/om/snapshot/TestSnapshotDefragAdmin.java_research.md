# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotDefragAdmin.java

## Purpose
`TestSnapshotDefragAdmin` verifies the `ozone admin om snapshot defrag` command can target OM leader and follower nodes in an HA cluster, with both synchronous and `--no-wait` invocation modes.

## Important APIs, Types, and Functions
Setup enables filesystem snapshots, sets `OZONE_SNAPSHOT_DEFRAG_SERVICE_INTERVAL`, limits per task via `SNAPSHOT_DEFRAG_LIMIT_PER_TASK`, and starts a 3-OM `MiniOzoneHAClusterImpl`. Tests call `executeDefragCommand(nodeId, noWait)`, which constructs an `OzoneAdmin`, imports cluster config, captures stdout, and executes `om snapshot defrag --service-id ... --node-id ...` optionally with `--no-wait`.

## Control Flow, State, and Persistence
The test locates the leader, finds a follower by comparing node IDs, iterates all OMs, and verifies command output. It does not create snapshots or inspect defrag results; it checks command dispatch and response text. The persistent state under test is primarily HA OM service registration and the admin command's ability to route to a target OM node.

## Dependencies and Integration Points
This is an admin CLI integration test covering HA service ID lookup, node ID targeting, snapshot defrag service trigger plumbing, and stdout messaging. It depends on `OzoneAdmin.execute` and cluster-provided configuration resources.

## Risks and Test Signals
The signal is command-level: exit code zero and output containing trigger/completion/background wording. It may miss defrag task correctness, queueing, and actual RocksDB/snapshot state changes. Risks include brittle stdout text assertions and follower routing behavior changing.
