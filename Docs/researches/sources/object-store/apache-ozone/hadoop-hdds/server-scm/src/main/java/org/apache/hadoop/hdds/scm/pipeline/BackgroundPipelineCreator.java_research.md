# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/BackgroundPipelineCreator.java

## Purpose
`BackgroundPipelineCreator` is an `SCMService` that periodically or reactively creates new pipelines when SCM leadership, safemode, and precheck conditions allow it.

## Important APIs, Types, And Functions
The constructor reads safemode pipeline-creation policy, post-safemode wait time, creation interval, and derives the leader-specific thread name. `start` creates a daemon-like named worker thread with an uncaught exception handler that shuts down SCM. `stop` interrupts and joins that thread. `run` loops while running, calling `shouldRun` and `createPipelines`. `notifyStatusChanged`, `notifyEventTriggered`, and `shouldRun` implement the `SCMService` contract. `createPipelines` builds replication configs from cluster defaults and asks `PipelineManager` to create pipelines until creation fails for each config.

## Control Flow
The service starts in `PAUSING`. `notifyStatusChanged` transitions to `RUNNING` only when SCM is leader-ready and either out of safemode or configured to create pipelines in safemode. Normal periodic execution waits until the post-safemode delay has elapsed. Certain events, including new node, node address update, unhealthy-to-healthy node, and precheck completion, set a one-shot flag and notify the monitor so creation can run immediately.

Pipeline creation chooses the configured default replication type. For non-EC types it iterates all nonzero replication factors; for EC default it still creates only Ratis factor-one support pipelines. Unsupported or disabled combinations are skipped. A looping iterator repeatedly tries configs and removes a config when creation throws, ending when all current configs fail.

## State And Persistence Behavior
The class owns thread lifecycle state, service status, one-shot trigger state, and timing fields. It does not persist pipeline records directly; successful creation is delegated to `PipelineManager`, which persists via `PipelineStateManager`. Thread state is protected by `AtomicBoolean`, a `ReentrantLock`, and a monitor object.

## Dependencies And Integration Points
It depends on SCM HA service events, `SCMContext` leadership/safemode/precheck state, `PipelineManager`, replication config helpers, and Ozone/HDDS config keys. `PipelineManagerImpl.newPipelineManager` creates and registers it with `SCMServiceManager`.

## Risks And Edge Cases
The creation loop can aggressively create pipelines until every config fails; placement failure is used as the stopping condition. If unexpected exceptions repeat, they are logged and the config is removed for that run, not retried until the next run. Interruption during monitor wait stops the service by setting `running` false. One-shot runs bypass post-safemode delay, so event sources must be intentional.

## Test Signals
Tests should validate service state transitions, one-shot event triggers, safemode creation settings, delayed post-safemode execution, start/stop idempotence, exception handling in creation loops, replication config selection for RATIS/STAND_ALONE/EC defaults, and SCM shutdown on uncaught worker errors.
