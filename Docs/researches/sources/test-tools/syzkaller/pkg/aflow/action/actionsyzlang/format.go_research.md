# sources/test-tools/syzkaller/pkg/aflow/action/actionsyzlang/format.go

## Purpose

`format.go` defines the `Format` action that validates and canonicalizes an LLM-generated syzkaller program before it is executed by reproduction workflows.

## Important APIs, Types, and Functions

`Format = aflow.NewFuncAction("syzlang-format", formatActionFunc)` exposes the action. `FormatArgs` contains `TargetOS`, `TargetArch`, and `CandidateReproSyz`; `FormatResult` returns `ReproSyz`. `formatActionFunc` resolves the syzkaller target, deserializes the candidate program with `prog.Strict`, and returns `p.Serialize()`.

## Control Flow

The function obtains the target first. It then strictly deserializes the candidate syz text, returning a contextual `failed to deserialize syzkaller program` error on invalid programs. On success, the serializer normalizes formatting, resource references, and target-specific program syntax.

## State and Persistence Behavior

The action has no persistent state, no filesystem writes, and no cache interaction. It transforms one state field into `ReproSyz` for later actions such as `crash.Reproduce`.

## Dependencies and Integration Points

It integrates `aflow` function actions with syzkaller `prog` target descriptions and the imported `sys` package. In the repro flow it is the validation gate between the LLM candidate and VM execution.

## Risks and Edge Cases

Strict deserialization rejects candidate syntax that non-strict paths might accept, so LLM output must be complete and target-correct. Empty candidates fail as deserialization errors. Target lookup errors propagate without extra context.

## Test Signals

Tests cover valid and invalid linux programs across amd64 and arm64 and assert unknown syscall errors are surfaced.
