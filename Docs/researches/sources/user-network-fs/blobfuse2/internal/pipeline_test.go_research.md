<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/pipeline_test.go -->
# sources/user-network-fs/blobfuse2/internal/pipeline_test.go

## Purpose
Unit tests for pipeline construction and basic lifecycle behavior using minimal in-package fake components.

## Important APIs, Types, and Functions
`ComponentA`, `ComponentB`, and `ComponentC` embed `BaseComponent` and return producer, mid, and consumer priorities. `ComponentStream` and `ComponentBlockCache` provide named test components for alias behavior. `pipelineTestSuite.SetupTest` registers these components through `AddComponent`. Tests cover `NewPipeline`, invalid priority ordering, unknown names, `Start`, `Stop`, and stream aliasing.

## Control Flow and State
The suite mutates the global component registry on each test setup. Valid pipelines use `ComponentA` then `ComponentB`. Invalid order uses `ComponentC` then `ComponentA` and asserts an "is out of order" error. Lifecycle test builds a two-component pipeline, starts it with `context.Background`, then stops it. Stream alias test registers both `"stream"` and `"block_cache"` and expects `NewPipeline([]string{"stream"})` to produce a component named `"block_cache"`.

## Dependencies and Integration Points
Uses `testify/suite` and `testify/assert`. The fake components rely on `BaseComponent` default implementations for configuration/start/stop/name behavior, so the suite indirectly tests compatibility between `Pipeline` and base component defaults.

## Risks and Edge Cases
The global registry is not cleared, so tests can be order-dependent if other package tests register the same names. It does not mock or assert `SetNextComponent` wiring directly. Error aggregation paths are not covered because fake components do not fail configure/start/stop. `print(p.components[0].Name())` is noisy in test output.

## Test Signals
Passing tests show the most common pipeline configuration path works and the legacy `stream` alias is preserved. Missing signals include empty config handling, duplicate names, lifecycle cleanup on partial start failure, and multiple stop errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/pipeline_test.go -->
