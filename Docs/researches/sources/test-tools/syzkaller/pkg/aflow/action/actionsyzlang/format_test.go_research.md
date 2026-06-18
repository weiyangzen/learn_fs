# sources/test-tools/syzkaller/pkg/aflow/action/actionsyzlang/format_test.go

## Purpose

`format_test.go` validates strict syzkaller program formatting behavior for candidate repros.

## Important APIs, Types, and Functions

`TestFormat` invokes `formatActionFunc` with `FormatArgs` and checks `FormatResult.ReproSyz`. It uses `testify/require` assertions.

## Control Flow

For amd64 and arm64, the test submits a valid `openat` plus `write` syz program and expects non-empty canonical output. It then submits an unknown syscall and expects an error containing `unknown syscall`.

## State and Persistence Behavior

The test is stateless and does not use aflow execution, cache, or filesystem state. It depends on syzkaller target descriptions being registered by package imports.

## Dependencies and Integration Points

It indirectly exercises `prog.GetTarget`, strict target deserialization, and serialization for linux syscall descriptions.

## Risks and Edge Cases

It does not check exact canonical formatting, only non-empty output, so serializer formatting regressions that still produce text may pass. It also does not test bad target names or empty candidates.

## Test Signals

The invalid syscall check is the strongest behavioral signal because it confirms strict validation catches LLM hallucinated syscall names.
