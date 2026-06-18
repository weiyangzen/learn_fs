# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestRatisPipelineLeader.java

## Purpose

`TestRatisPipelineLeader` verifies that SCM pipeline metadata reflects Ratis leader identity and updates after leadership changes. It protects client routing assumptions that depend on pipeline leader information.

## Important APIs, Types, And Functions

The class starts a MiniOzoneCluster, obtains RATIS pipelines, and uses `Pipeline`, `PipelineManager`, and datanode/Ratis leader inspection. Tests are `testLeaderIdUsedOnFirstCall`, `testLeaderIdAfterLeaderChange`, and helper `verifyLeaderInfo`.

## Control Flow

Setup starts the cluster. The first test validates that initial pipeline retrieval includes leader ID. The second forces or waits for a leader change, retrieves pipeline metadata again, and verifies SCM reports the new leader. The helper compares SCM pipeline leader metadata with the Ratis group state.

## State And Persistence Behavior

Pipeline state is maintained in SCM and backed by Ratis leader election inside datanode pipelines. The test observes volatile leader state rather than durable key data.

## Dependencies And Integration Points

It integrates SCM pipeline manager, MiniOzoneCluster datanodes, Ratis consensus state, and pipeline metadata returned to clients.

## Risks And Test Signals

Failures indicate stale pipeline leader caching, missing leader detection on first lookup, or inability to refresh metadata after Ratis leadership changes. Timing around leader election is the main risk.
