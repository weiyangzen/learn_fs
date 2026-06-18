# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/MockPipelineManager.java

Purpose: lightweight test implementation of `PipelineManager` backed by a real `PipelineStateManager`. It lets tests create, query, and mutate pipelines without starting the full production pipeline manager.

Important APIs and types: implements `PipelineManager`; owns `PipelineStateManager` and `NodeManager`. It creates RATIS-style mock pipelines with random datanodes, EC pipelines with required-node counts, read pipelines from `ContainerReplica` sets and replica indexes, and delegates pipeline lookup, counts, container membership, open/close/deactivate transitions, and space allocation checks to `PipelineStateManager`/`NodeManager`.

Control flow: constructor builds `PipelineStateManagerImpl` from a DB table, SCM HA Ratis server, transaction buffer, and node manager. `createPipeline` branches on replication type: EC calls `buildECPipeline`; non-EC builds a three-node open pipeline. The created pipeline protobuf is added to state. Read pipeline creation copies replica datanodes and replica indexes into a closed pipeline. Many lifecycle methods are intentionally no-ops.

State and persistence behavior: pipeline metadata is stored through the `PipelineStateManager` and the supplied RocksDB table/transaction buffer. Container-to-pipeline relationships are delegated to the state manager. Deletion, scrub, creator start/trigger, freeze/resume, locks, metrics, and pipeline info do not maintain state in this mock.

Dependencies and integration points: integrates tests with `SCMDBDefinition.PIPELINES`, `SCMHAManager`, `NodeManager.checkSpaceAndRecordAllocation`, `ContainerReplica`, `ClientVersion`, and Ozone replication configs.

Risks and edge cases: because several `PipelineManager` methods are no-ops or return null/defaults, this mock is suitable only for tests that do not need production lifecycle, locking, metrics, deletion, or safe-mode semantics. Non-EC `createPipeline` ignores favored/excluded nodes. `deletePipeline` leaves state untouched.

Test signals: not itself a test, but it is a reusable fixture. Its value is preserving realistic state-manager behavior while isolating tests from production scheduling and SCM services.
