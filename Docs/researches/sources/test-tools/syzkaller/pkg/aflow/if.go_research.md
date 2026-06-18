# sources/test-tools/syzkaller/pkg/aflow/if.go

## Purpose

`if.go` implements aflow's conditional action node. It chooses between `Do` and optional `Else` based on a workflow state value and reconciles branch outputs so downstream actions see stable fields.

## Important APIs, Types, and Functions

`If` has `Condition`, `Do`, `Else`, and internal `ifVars`. Methods are `execute`, `verify`, and `verifyOutputs`.

## Control Flow

Execution looks up the condition in `ctx.state`, treats non-zero values as true, and gives slices/maps/arrays/channels special truthiness based on length. It records an `If` span with condition arg, executes `Do` or `Else`, and on success fills any branch-only outputs absent from the executed branch with zero values recorded during verification. Verification checks the condition input, verifies branches, ensures branch-only outputs are represented, and rejects incompatible output types.

## State and Persistence Behavior

The action mutates the in-memory state map by adding outputs from the executed branch and zero-valued placeholders for non-executed branch outputs. It has no filesystem or cache state.

## Dependencies and Integration Points

It depends on reflection, state verification, maps cloning, and trajectory spans. Patch iteration and C-repro workflows use nested `If` nodes for conditional LLM/tool branches.

## Risks and Edge Cases

Truthiness uses `reflect.IsZero`, with container length overriding non-nil empty slices/maps to false. Channels are checked by length, which is usually zero and may be surprising. Verification mutates `ifVars` on the `If` object, so action objects are not immutable after registration.

## Test Signals

`if_test.go` covers truthiness for strings, bools, ints, slices, nil/empty slices, else branches, missing condition, and branch output mismatch errors.
