# sources/test-tools/syzkaller/pkg/aflow/flow/common/prompts.go

## Purpose

`prompts.go` loads embedded prompt files and applies shared prompt substitutions.

## Important APIs, Types, and Functions

`Prompt(fs embed.FS, name string) string` reads a file, replaces `{{.CommonInstructionDontMakeAssumptions}}` with the trimmed shared instruction, trims whitespace, and panics on read failure or empty prompt.

## Control Flow

The function reads from the supplied embedded filesystem, performs a global string replacement, trims the final prompt, validates non-empty content, and returns it. It intentionally panics because prompts are static build-time resources and broken prompt paths should fail early.

## State and Persistence Behavior

No runtime state is persisted. Prompt content is embedded in binaries by caller packages.

## Dependencies and Integration Points

It uses `embed.FS`, `fmt`, `strings`, and the shared instruction constant. All concrete workflows with markdown prompt files use it to produce `LLMAgent.Instruction`.

## Risks and Edge Cases

Panics during package initialization or registration can take down the process when prompt files are missing or empty. Replacement is literal and global, so prompt authors must use the exact placeholder spelling.

## Test Signals

Tests validate successful substitution and panic on empty prompt files.
