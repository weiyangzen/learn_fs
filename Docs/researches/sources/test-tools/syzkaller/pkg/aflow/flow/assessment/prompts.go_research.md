# sources/test-tools/syzkaller/pkg/aflow/flow/assessment/prompts.go

## Purpose

`prompts.go` embeds the markdown prompt files used by assessment workflows.

## Important APIs, Types, and Functions

The single package variable is `prompts embed.FS`, populated by `//go:embed prompts/*.md`.

## Control Flow

There is no runtime control flow in this file beyond Go embed initialization. Other files pass this `embed.FS` to `common.Prompt`.

## State and Persistence Behavior

Prompt text is compiled into the binary. Changes to prompt files require rebuild and can alter workflow behavior without Go code changes.

## Dependencies and Integration Points

It depends on the standard `embed` package and is consumed by KCSAN, moderation, and security assessment registrations.

## Risks and Edge Cases

Missing prompt files break the build at compile time or panic at prompt load depending on path usage. Empty prompt contents are caught by `common.Prompt`.

## Test Signals

Prompt loading behavior is tested in `flow/common/prompts_test.go`, not specifically for assessment prompt files.
