# sources/test-tools/syzkaller/pkg/aflow/tool/grepper/grepper_test.go

## Purpose
Linux-only tests for the grepper tool against a synthetic git repository.

## Important APIs, Types, and Functions
Uses `vcs.MakeTestRepo`, `aflow.TestTool`, and assertions on output strings.

## Control Flow
The test commits several files, then searches for normal matches, long-line matches, excessive matches, no matches, invalid regexes, path-restricted results, and dash-prefixed expressions.

## State and Persistence Behavior
Temporary repository only; no durable side effects.

## Dependencies and Integration Points
Depends on git behavior and Linux-specific error messages. It validates the user-facing output format expected by LLM agents.

## Risks and Test Signals
Good signal for truncation and error normalization. It may be sensitive to git version wording for invalid regex diagnostics.
