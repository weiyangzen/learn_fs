# sources/test-tools/syzkaller/pkg/aflow/flow/flows.go

## Purpose

`flows.go` is the aggregate import package that registers all built-in aflow workflows through blank imports.

## Important APIs, Types, and Functions

The file has no exported APIs. It blank-imports `flow/assessment`, `flow/patching`, `flow/repro`, and `flow/reproc`.

## Control Flow

Importing package `flow` triggers the `init` functions in all concrete workflow packages, which call `aflow.Register` and populate `aflow.Flows`.

## State and Persistence Behavior

The side effect is process-global workflow registration. No other state is stored in this file.

## Dependencies and Integration Points

Dashboard/job runners can import this package when they want all standard workflows registered. Tests import it to verify registration and MCP tool naming.

## Risks and Edge Cases

Blank imports hide registration side effects. Adding/removing imports changes which workflows are available at runtime. Registration panics in any imported package prevent package initialization.

## Test Signals

`flows_test.go` imports this package and thereby verifies all registrations complete.
