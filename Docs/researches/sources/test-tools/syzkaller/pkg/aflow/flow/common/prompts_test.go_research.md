# sources/test-tools/syzkaller/pkg/aflow/flow/common/prompts_test.go

## Purpose

`prompts_test.go` verifies common prompt loading, shared instruction substitution, trimming, and empty prompt rejection.

## Important APIs, Types, and Functions

The file embeds `test_prompts/*.md` into `testPrompts`. `TestPrompt` calls `Prompt` and compares exact output. `TestPromptEmpty` asserts `Prompt` panics for an empty prompt.

## Control Flow

`TestPrompt` loads a fixture containing the common placeholder and expects it to be replaced with the multi-line source-code assumption instruction. `TestPromptEmpty` wraps the call in `require.Panics`.

## State and Persistence Behavior

Prompt fixtures are compile-time embedded. No filesystem writes or persistent state are used.

## Dependencies and Integration Points

It uses Go embed and `testify/require`. The test is a local signal for the prompt infrastructure used by assessment and patching workflows.

## Risks and Edge Cases

Exact string comparison will catch whitespace changes in the shared instruction or trimming logic. It does not test missing file paths.

## Test Signals

These tests strongly guard the behavior relied on by workflow registration when loading prompt markdown.
