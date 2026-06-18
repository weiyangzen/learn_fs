# sources/test-tools/syzkaller/pkg/aflow/if_test.go

## Purpose

`if_test.go` validates conditional execution truthiness, else behavior, zero-value output filling, and registration-time branch errors.

## Important APIs, Types, and Functions

`TestIf` builds simple actions with `NewFuncAction` and wraps them in `If`. `TestIfErrors` uses `testRegistrationError` to assert verifier failures.

## Control Flow

The true/false tests cover strings, booleans, integers, non-empty slices, empty slices, nil slices, and explicit else branches. Error tests check empty condition, missing condition input, output produced only by Else, and output type disagreement between Do and Else.

## State and Persistence Behavior

The tests run in the aflow test harness with no persistent state. Golden trajectory output may be managed by the shared harness outside this file.

## Dependencies and Integration Points

They depend on `testFlow`, `NewFuncAction`, and the verifier. They protect control-flow semantics used by patch and repro workflows.

## Risks and Edge Cases

The tests do not cover maps, arrays, or channels, though code supports them. They assume zero string output for non-executed branches.

## Test Signals

Coverage is strong for common workflow conditions and branch dataflow validation.
