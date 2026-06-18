# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachine.java

## Purpose
This test class validates two single-datanode container state-machine behaviors: corrupting a container directory during a write marks the container unhealthy, and RATIS snapshot retention stays bounded when the snapshot threshold is low.

## Important APIs, types, and functions
The setup enables block tokens and OM test security, uses test certificate and secret-key clients, sets snapshot threshold to one, disables stream buffer flush delay, and creates a one-datanode RATIS pipeline. It uses `ContainerStateMachine`, `SimpleStateMachineStorage`, `StatemachineImplTestUtil`, `RatisServerConfiguration`, `FileUtil.fullyDelete`, `OzoneManager.startSecretManager`, and `TestHelper.getStateMachine`.

## Control flow
`testContainerStateMachineFailures` creates a RATIS/ONE key, writes and flushes data to create a container, writes again, captures the single `OmKeyLocationInfo`, deletes the corresponding container directory, and lets try-with-resources close the stream. After close it asserts the datanode's container state is `UNHEALTHY`.

`testRatisSnapshotRetention` starts by asserting no latest snapshot. It writes ten keys, each with a flush and second write, then inspects the snapshot directory and verifies the number of retained snapshots is within one of configured retention. It writes ten more keys and asserts the count remains bounded.

## State and persistence behavior
The first test mutates on-disk container contents and observes in-memory container state. The second test observes RATIS snapshot files under `SimpleStateMachineStorage` and asserts cleanup/retention behavior after repeated state-machine transactions. Both tests use real persisted state in MiniOzoneCluster storage directories.

## Dependencies and integration points
Integration includes secure client setup, OM secret manager, datanode container set, RATIS state machine storage, and Ozone client writes. The static `getSnapshotPath` helper is also used by nearby state-machine tests.

## Risks and test signals
Because snapshot creation and deletion can be asynchronous, the retention check allows an off-by-one difference. The unhealthy-container test depends on close-time failure detection after deleting a directory. Strong signals are exact `UNHEALTHY` state and bounded snapshot file count before and after additional writes.
