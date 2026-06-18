# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineDatanodesIntersection.java

Purpose: stress-style parameterized test that creates many RATIS/THREE pipelines and detects when newly-created pipelines contain the same datanode set as existing ones.

Important APIs and types: uses `MockNodeManager`, `PipelineStateManagerImpl`, `MockRatisPipelineProvider`, `RatisPipelineUtils.checkPipelineContainSameDatanodes`, `SCMHAManagerStub`, RocksDB `DBStore`, and pipeline-limit configuration.

Control flow: for each `(nodeCount, nodeHeaviness)` case, the test configures a mock node manager and pipeline limit, creates a state manager, then loops creating pipelines until `SCMException` or the theoretical node-count times heaviness bound. Each pipeline is persisted to state, added to node manager, and checked for overlap with previous pipelines. Intersections are logged rather than asserted.

State and persistence behavior: pipelines are stored in the test RocksDB-backed state manager and also registered in mock node manager pipeline mappings. The `end` flag controls the creation loop and is reset afterward.

Dependencies and integration points: exercises the Ratis pipeline provider against pipeline state, node pipeline load accounting, SCM DB definitions, and overlap utility logic.

Risks and edge cases: the test has no assertion on `intersectionCount`, so it mainly detects unexpected exceptions other than expected capacity exhaustion. It logs overlap information but does not fail on duplicate datanode sets. Loop count can be high for larger parameters.

Test signals: weak but useful stress signal that pipeline creation runs to capacity without regular IO failures and that overlap detection can inspect created pipelines.
