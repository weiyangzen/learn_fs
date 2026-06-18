# sources/test-tools/syzkaller/pkg/aflow/func_action.go

## Purpose

`func_action.go` adapts ordinary typed Go functions into aflow actions that consume and produce named workflow state fields.

## Important APIs, Types, and Functions

`NewFuncAction[Args, Results]` creates a `funcAction`, registers it for MCP, and returns it as `Action`. `funcAction.execute` converts `ctx.state` into `Args`, records an action span, calls the function, converts results to a map, merges outputs into state, and finishes the span. `verify` checks name, required inputs, and provided outputs. `testVerify` supports the test harness.

## Control Flow

At execution time, arguments are populated from current state using schema conversion. The action span starts before invoking user code. Results are inserted into both the span and context state before `finishSpan`, even when the function returns an error.

## State and Persistence Behavior

The only persistent side effect here is global MCP action registration. Runtime state mutation is limited to inserting result fields into `ctx.state`; any filesystem/cache effects come from the wrapped function.

## Dependencies and Integration Points

It depends on schema conversion helpers, verification helpers, trajectory spans, and MCP registration. All non-LLM workflow steps in the assigned flows use this adapter.

## Risks and Edge Cases

Results are inserted even if `fnErr` is non-nil, which can be useful for partial diagnostics but may surprise downstream logic if errors are handled differently. Conversion requires field names/types to match state. Empty action names are registration errors.

## Test Signals

The broad flow tests exercise function actions in pipelines, const consumption, and verifier behavior.
