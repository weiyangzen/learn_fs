<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json

## Purpose
This large trajectory fixture is the expected execution trace for `TestLLMToolMaxIters` in `llm_tool_test.go`. It proves that an `LLMTool` sub-agent can perform exactly `maxLLMIterations` internal tool loops before returning to the parent `LLMAgent`, and that the framework still finishes with the parent reply `YES`.

## Important APIs, Types, and Functions
The fixture serializes `trajectory.Span` objects from `pkg/aflow/trajectory`. It exercises `LLMAgent`, `LLMTool`, `Tool`, `NewFuncTool`, and the `maxLLMIterations` constant in `llm_agent.go`. The sub-agent tool declaration is `researcher-tool` with integer argument `Arg`; the parent-visible tool is `researcher` with `Question` input and `Answer` output.

## Control Flow
The JSON array has 1014 spans: 2 flow spans, 6 parent-agent spans, 506 LLM spans, and 500 tool spans. The sequence starts with flow `test`, parent agent `smarty`, a parent LLM call that invokes `researcher`, then a nested agent named `researcher`. The nested agent alternates LLM/tool spans for `researcher-tool` 250 times. After the final sub-agent LLM reply `Nothing.`, control returns through the `researcher` tool result and the parent agent replies `YES`.

## State and Persistence
This file is static golden data. It persists deterministic span sequence numbers, nesting levels, model names, instructions, prompts, tool args/results, and final flow results. It does not mutate runtime state itself, but guards state propagation through `ctx.state` for `LLMTool`, especially the temporary `AFLOW_LLMTOOL_PROMPT` and `AFLOW_LLMTOOL_REPLY` variables.

## Dependencies and Integration Points
The fixture integrates with the aflow test harness that records trajectories and compares them against `testdata`. It depends on the generated span schema staying compatible with `trajectory.Span`, and on the test's fake LLM reply list matching the expected number of iterations.

## Risks
Because the file is large and sequence-sensitive, small changes to retry or span-recording behavior can produce broad diffs. A regression in max-iteration enforcement could either truncate before the sub-agent result or allow unbounded loops. Changes to tool nesting, span names, or LLMTool state cleanup would break this fixture.

## Test Signals
Successful comparison signals that nested LLM tools can reach the configured iteration ceiling, record 250 internal tool calls, return `Answer: Nothing.`, and let the parent flow finish with `Reply: YES` without span errors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json -->
