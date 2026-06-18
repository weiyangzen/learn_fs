# sources/test-tools/syzkaller/pkg/aflow/flow/assessment/moderation.go

## Purpose

`moderation.go` registers a moderation workflow that judges whether a bug report is internally consistent and actionable.

## Important APIs, Types, and Functions

`moderationInputs` includes target, bug title, crash report, and kernel repo/commit/config fields. The init function registers `ai.WorkflowModeration` producing `ai.ModerationOutputs`. The LLM structured output is `Actionable`.

## Control Flow

The pipeline checks out/builds the kernel, prepares a code search index, runs an `LLMAgent` named `expert` with the embedded moderation instruction and crash report prompt, uses `common.CodeAccessTools`, and word-wraps the raw explanation.

## State and Persistence Behavior

State follows normal aflow dataflow. Kernel source/build outputs are cached. The final `Actionable` and formatted `Explanation` are persisted as moderation outputs.

## Dependencies and Integration Points

It depends on kernel actions, codesearcher, common prompt substitution, embedded prompts, and aflow LLM structured outputs.

## Risks and Edge Cases

The prompt only includes `CrashReport` despite `BugTitle` being an input, so title-specific context is not directly shown unless report includes it. Build/index failures prevent moderation output even for reports that could perhaps be assessed text-only.

## Test Signals

No direct semantic tests exist. Package import through `flow/flows.go` triggers registration verification.
