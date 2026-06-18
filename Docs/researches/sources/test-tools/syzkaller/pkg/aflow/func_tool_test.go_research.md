# sources/test-tools/syzkaller/pkg/aflow/func_tool_test.go

## Purpose

`func_tool_test.go` verifies tool error semantics and per-run duplicate-call history behavior.

## Important APIs, Types, and Functions

Tests include `TestToolErrors`, `TestToolLoopDetection`, `TestToolHistorySequentialLeak`, and helper `newTestContext`.

## Control Flow

`TestToolErrors` has a tool return first `BadCallError` and then a hard error, verifying the former is sent to the LLM and the latter aborts with diagnostic args. `TestToolLoopDetection` directly checks duplicate-call thresholds in `agentSession.recordAndCheckDuplicate`. `TestToolHistorySequentialLeak` runs the same agent in two fresh contexts and asserts duplicate-call history does not leak between executions.

## State and Persistence Behavior

Tests use stub contexts with temp caches and stubbed model responses. Duplicate tool history is expected to be session-local, not stored on `LLMAgent`.

## Dependencies and Integration Points

They depend on `LLMAgent`, `NewFuncTool`, GenAI function call parts, and aflow test execution helpers.

## Risks and Edge Cases

The duplicate-call tests rely on exact default limits. `newTestContext` creates a zero-size cache and no-op event callback, so it is suitable for LLM stubs but not for cache behavior tests.

## Test Signals

These tests specifically guard a subtle state leak risk where tool histories from one run could block valid tool calls in later runs.
