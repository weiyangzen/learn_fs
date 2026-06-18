# sources/test-tools/syzkaller/pkg/aflow/flow/reproc/reproc_test.go

## Purpose

`reproc_test.go` covers deterministic helper behavior for the C reproducer workflow.

## Important APIs, Types, and Functions

Tests call `FormatCFunc`, `TruncateLogFunc`, `LoopControllerFunc`, `extractCCode`, and `validateOracleOutputs` using `aflow.NewTestContext`.

## Control Flow

The tests validate C formatting returns non-empty output, log truncation preserves short logs and crash report, loop controller handles success, collision, successful/failed probes, preservation of capability state, and terminal errors, code extraction handles C fenced blocks/plain fenced blocks/no fences/multiple blocks, and oracle validation enforces probe/repro feedback requirements.

## State and Persistence Behavior

All tests are in-memory except `FormatCFunc`, which may use csource formatting internals. No VM, cache, or file save behavior is exercised.

## Dependencies and Integration Points

They use aflow test context and `testify/assert`. The tests protect workflow loop logic independently of LLM and VM execution.

## Risks and Edge Cases

The tests do not compile generated C, run strace, validate generator output state, or test `SaveReproC`. Multiple fenced code extraction intentionally picks the first block.

## Test Signals

The strongest signals are validation rules that force oracle feedback on failed probes/collisions/non-reproduction and prevent inconsistent terminal/probe states.
