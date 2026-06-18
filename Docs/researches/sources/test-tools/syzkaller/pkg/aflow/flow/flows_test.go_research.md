# sources/test-tools/syzkaller/pkg/aflow/flow/flows_test.go

## Purpose

`flows_test.go` verifies package-level workflow registration and MCP tool naming after all workflow packages are imported.

## Important APIs, Types, and Functions

`TestMCPTools` iterates `aflow.MCPTools`, logs each tool name, and fails if an MCP tool name contains `-`.

## Control Flow

The test's package import triggers all blank-imported flow registrations. It then checks the already-populated global MCP tool registry.

## State and Persistence Behavior

It reads global `aflow.MCPTools` state populated during init. It does not mutate persistent storage.

## Dependencies and Integration Points

It depends on the aggregate `flow` package side effects and aflow MCP registration behavior.

## Risks and Edge Cases

The test enforces an MCP naming restriction that differs from Gemini tool names, where hyphens are permitted. It does not verify that every expected workflow exists, only that registration did not panic and MCP tool names satisfy the dash rule.

## Test Signals

The most important signal is implicit: if any workflow has broken dataflow verification, package init panics and the test binary fails before or during this test.
