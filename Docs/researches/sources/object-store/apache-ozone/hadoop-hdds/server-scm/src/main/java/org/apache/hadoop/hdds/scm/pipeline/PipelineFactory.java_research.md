# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineFactory.java

## Purpose
`PipelineFactory` selects the appropriate `PipelineProvider` for a replication type and validates newly created pipelines.

## Important APIs, Types, And Functions
The main constructor installs providers for `STAND_ALONE`, `RATIS`, and `EC`. EC placement policy is obtained from `ContainerPlacementPolicyFactory.getECPolicy`. `create(replicationConfig, excludedNodes, favoredNodes)` delegates to the provider and validates non-null pipeline and required node count. `create(replicationConfig, nodes)` creates provider-specific pipelines from explicit nodes. `createForRead` delegates read-pipeline construction. `close` routes close behavior to the provider. Testing hooks expose and replace providers.

## Control Flow
Provider selection is a map lookup by `replicationConfig.getReplicationType()`. New write pipeline creation performs post-provider validation. Failures are surfaced as `SCMException` with internal-error or failed-to-find-healthy-nodes result codes. Provider construction fails fast with `RuntimeException` if EC placement policy cannot be created.

## State And Persistence Behavior
The factory holds an in-memory provider map. It does not persist pipelines; it returns objects to `PipelineManagerImpl`, which adds them to state and persistence.

## Dependencies And Integration Points
It depends on `NodeManager`, `PipelineStateManager`, configuration, SCM event publishing, SCM context, container placement metrics, and provider implementations. It is owned by `PipelineManagerImpl`.

## Risks And Edge Cases
A missing provider for a replication type causes null dereference rather than a clean unsupported-type exception. The node-count validation applies only to placement-aware create, not explicit-node create or read-pipeline create. Provider replacement in tests can bypass production invariants.

## Test Signals
Tests should validate provider registration, EC placement policy failure behavior, null pipeline detection, node-count mismatch detection, close delegation, and unsupported replication-type handling if new types are introduced.
