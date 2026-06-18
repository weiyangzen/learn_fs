# sources/test-tools/syzkaller/pkg/aflow/func_tool.go

## Purpose

`func_tool.go` adapts typed Go functions into tools callable by `LLMAgent`. It generates JSON schemas for tool parameters/results, separates hidden workflow state from LLM-provided args, and distinguishes recoverable bad tool calls from hard workflow failures.

## Important APIs, Types, and Functions

`NewFuncTool[State, Args, Results]` creates a `funcTool` and registers it for MCP. `BadCallError` wraps errors that should be returned to the LLM. `funcTool.declaration` returns a GenAI `FunctionDeclaration`; `execute` converts state and args, calls the Go function, and converts results. `verify`, `testVerify`, and `checkFuzzTypes` support registration and tests.

## Control Flow

When an LLM calls a tool, aflow converts hidden `State` from current workflow state in non-strict tool mode, converts LLM args also in non-strict mode to tolerate extra fields, invokes `Func`, and returns map results plus any error. `LLMAgent.callTools` decides whether `BadCallError` is fed back to the model or a hard error aborts the workflow.

## State and Persistence Behavior

The adapter itself has no persistent runtime state beyond MCP registration. Tool functions may read/cache/mutate through `*Context`.

## Dependencies and Integration Points

It depends on GenAI function declarations, JSON schema helpers, aflow schema conversion, verification, and MCP registration. Code search, syzlang, git, patchdiff, and other workflow tools use this abstraction.

## Risks and Edge Cases

Tool args are intentionally parsed non-strictly, so hallucinated extra fields are ignored rather than rejected. Missing or mistyped required fields still become errors. `BadCallError` should be used carefully so genuine infrastructure failures are not hidden as LLM-correctable mistakes.

## Test Signals

`func_tool_test.go`, `flow_test.go`, and `llm_agent_test.go` cover bad calls, hard errors, duplicate call detection, nil args, schema verification, and tool state isolation.
