# sources/test-tools/syzkaller/pkg/aflow/ai/ai.go

## Purpose

`ai.go` defines stable workflow type names and dashboard-facing output structs shared by `pkg/aflow/...` and dashboard packages. It is the schema contract for persisted AI workflow results.

## Important APIs, Types, and Functions

`WorkflowType` enumerates `patching`, `patch-iteration`, `moderation`, `assessment-kcsan`, `assessment-security`, `repro`, and `repro-c`. Output structs include `PatchingOutputs`, `PatchIterationOutputs`, `AssessmentKCSANOutputs`, `AssessmentSecurityOutputs`, `ModerationOutputs`, `ReproOutputs`, and `ReproCOutputs`. Shared value types include `Recipient`, `FixesTag`, `EmailTag`, `ExternalComment`, `PatchHistoryEntry`, and `CommentReply`.

## Control Flow

The file contains data definitions only. Control flow is created elsewhere by `aflow.Register`, which binds workflow types to concrete `Flow`s and uses these structs to extract typed outputs.

## State and Persistence Behavior

Comments warn that workflow type strings and output struct fields are stored in the dashboard database. Renaming/removing fields or changing string constants can break old persisted jobs and dashboard predicates.

## Dependencies and Integration Points

It imports `time` for external comment timestamps. The types are consumed by flow registration, dashboard config predicates, email/tag handling, and UI/API persistence.

## Risks and Edge Cases

Schema evolution is the main risk. Adding fields is relatively safe, but deleting or renaming fields requires migration or backward-compatibility handling. `AssessmentSecurityOutputs` is explicitly used in dashboard config predicates, making it especially sensitive.

## Test Signals

There are no direct tests for this schema file. Registration tests indirectly verify field names match produced workflow outputs.
