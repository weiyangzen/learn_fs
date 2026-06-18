<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/pipeline.go -->
# sources/user-network-fs/blobfuse2/internal/pipeline.go

## Purpose
Builds and controls an ordered chain of Blobfuse2 components. It converts configured component names into initialized `Component` instances, validates priority ordering, links them, and starts/stops them in lifecycle-safe order.

## Important APIs, Types, and Functions
`Pipeline` stores `components []Component` and `Header Component`. `NewComponent` is the constructor signature registered by components. `registeredComponents` maps component names to constructors. `GetComponent` returns a fresh component by name. `NewPipeline` configures components from string names. `Create` links components through `SetNextComponent`. `Start` calls `Create` and starts components from tail to head. `Stop` stops components from head to tail. `AddComponent` registers constructors. `init` initializes the registry.

## Control Flow and State
`NewPipeline` begins with the producer priority as the last accepted priority. For each configured name, it maps legacy `"stream"` to `"block_cache"` and sets `common.IsStream = true`, looks up the constructor, calls `Configure(isParent)`, and rejects components whose priority increases relative to the previous component. Successfully configured components are retained in order. `Create` sets `Header` to the first component and links every component to its successor. `Start` starts downstream components first; on a start error it stops already-started downstream components and returns `errors.Join` of all lifecycle errors. `Stop` attempts every component and joins errors.

## Dependencies and Integration Points
Depends on the internal `Component` interface and `ComponentPriority` ordering, `common.IsStream`, and `common/log` for diagnostics. It is central to config-driven assembly for libfuse, caches, storage backends, loopbackfs, xload, and other registered components.

## Risks and Edge Cases
`Create` assumes at least one component; an empty component list would panic. `registeredComponents` is global and unsynchronized, so concurrent registration or tests sharing names can interfere. `"stream"` is only special-cased in `NewPipeline`; callers of `GetComponent("stream")` do not get the alias behavior. Priority comparison relies on the numeric ordering semantics of `ComponentPriority`. `Start` continues its outer loop after an error, so multiple components can be started/stopped after an initial failure; this is intentional for error aggregation but can surprise tests.

## Test Signals
`pipeline_test.go` covers valid construction, invalid ordering, unknown components, lifecycle start/stop, and stream-to-block-cache mapping. Additional useful tests would cover empty pipelines, configure/start/stop error aggregation, and registry isolation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/pipeline.go -->
