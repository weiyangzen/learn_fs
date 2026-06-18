# sources/test-tools/syzkaller/pkg/aflow/flow_test.go

## Purpose

`flow_test.go` is the main integration-style unit test suite for the aflow runtime. It verifies typed dataflow, function actions, LLM agents, tools, candidates, structured outputs, missing input errors, quota reset time, tool misbehavior handling, flow consts, and registration errors.

## Important APIs, Types, and Functions

`TestWorkflow`, `TestNoInputs`, `TestQuotaResetTime`, `TestToolMisbehavior`, `TestFlowConsts`, and `TestFlowRegistrationErrors` are the main tests. They use `testFlow`, `NewFuncAction`, `LLMAgent`, `LLMOutputs`, `NewFuncTool`, `Pipeline`, and GenAI stub responses.

## Control Flow

`TestWorkflow` builds a multi-step pipeline with function action, LLM with parallel tool calls and `set-results`, another action, multi-candidate LLM, and aggregator. It verifies state propagation, numeric conversion from JSON float64, thoughts/replies, arrays from candidates, and template ranges. `TestToolMisbehavior` feeds wrong tool args, missing args, extra args, nonexistent tools, bad set-results, missing final replies, and eventual success. Registration tests assert precise verifier errors for const conflicts and unused consts.

## State and Persistence Behavior

Tests run with temporary workdirs and stubbed model responses. Golden trajectory files are handled by the broader test harness, while this file focuses on expected outputs/errors.

## Dependencies and Integration Points

It integrates nearly all aflow runtime pieces: schema conversion, verification, execution, trajectory spans, LLM parsing, tool execution, and cache-backed model stubs.

## Risks and Edge Cases

The tests are tightly coupled to exact error strings and model response sequencing. They do not call real model APIs. Complex LLM runtime behaviors such as token compression are tested in `llm_agent_test.go`.

## Test Signals

This is a high-value regression suite for core dataflow semantics and LLM/tool protocol handling.
