# sources/test-tools/syzkaller/pkg/aflow/trajectory/html/trajectory_test.go

## Purpose
Tests inferred tool-call attribution for trajectory HTML view models.

## Important APIs, Types, and Functions
Uses `UIAITrajectorySpan` and `PopulateToolCalls` with testify assertions.

## Control Flow
Tests cover one tool before an LLM, multiple consecutive tools before an LLM, and nested agents where tool calls at one nesting level must not leak to another.

## State and Persistence Behavior
Pure in-memory tests. No rendered files are written.

## Dependencies and Integration Points
Protects the UI tooltip/chart data computed by `trajectory.go`.

## Risks and Test Signals
Good signal for nesting isolation and pending-tool clearing. It does not validate template rendering or JSON escaping.
