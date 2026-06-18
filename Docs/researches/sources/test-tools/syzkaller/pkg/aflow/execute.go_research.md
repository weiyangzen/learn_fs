# sources/test-tools/syzkaller/pkg/aflow/execute.go

## Purpose

`execute.go` is the main runtime for executing registered aflow workflows. It validates inputs, constructs execution context, manages cache/temp lifecycle, records trajectory spans, calls Gemini/Vertex models, classifies quota/token errors, and exposes helpers used by actions and tools.

## Important APIs, Types, and Functions

`(*Flow).Execute` runs a workflow. Error helpers include `FlowError`, `IsFlowError`, `IsModelQuotaError`, `isInputTokenOverflowError`, `isOutputTokenOverflowError`, and `QuotaResetTime`. `Context` carries `context.Context`, workdir, model override, cache, state map, event callback, span counters, and test stubs. Cache helpers include `Context.Cache`, `CacheObject`, `RetrieveObject`, `CacheReadObject`, `TempDir`, and `Close`. Model functions include `generateContentGemini` and `loadModelList`.

## Control Flow

`Execute` converts inputs to the workflow input struct, clones them, inserts consts, builds `Context`, installs test stubs/default time/model functions, starts a flow span, executes the root action, records extracted outputs on success, finishes the span, checks span nesting balance, and returns outputs. `generateContentGemini` lazily initializes a singleton model client/list, checks model existence, caps temperature to model metadata, disables thinking for non-thinking models, applies a 10-minute request timeout, and maps deadline hangs to retry errors. `loadModelList` chooses exactly one backend from environment variables and either hardcodes Vertex model metadata or queries Gemini Developer API models.

## State and Persistence Behavior

Workflow state is a mutable `map[string]any` scoped to one execution. Cache dirs and temp dirs are tracked in the context and released/removed by `Close`. Model client/list are process-global singletons. Trajectory spans are emitted through `onEvent` at start and finish with sequence and nesting.

## Dependencies and Integration Points

It uses `google.golang.org/genai`, syzkaller `osutil`, trajectory records, and aflow schema conversion helpers. All actions/tools depend on `Context`. Dashboard/job runners depend on `Flow.Execute` and `FlowError` to separate expected workflow failures from infrastructure failures.

## Risks and Edge Cases

Only one of `GOOGLE_API_KEY`, `GOOGLE_VERTEX_API_KEY`, or `GOOGLE_CLOUD_PROJECT` may be set. `onEvent` must be non-nil and reliable because span start/finish errors abort execution. The global model list is initialized once, so environment changes during process lifetime are ignored. Cache must be supplied; nil cache would panic in cache helpers. `RetrieveObject` intentionally rejects non-local or malformed IDs.

## Test Signals

`flow_test.go` covers workflow execution, missing inputs, quota reset time, const handling, and span-driven stubs. `cache_test.go` covers cache helpers. LLM tests exercise model error classification through lower-level functions.
