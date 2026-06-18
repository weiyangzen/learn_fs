# sources/test-tools/syzkaller/pkg/aflow/tool/patchdiff/patchdiff.go

## Purpose
Implements an aflow tool that shows the current scratch-source patch with `git diff` so agents can inspect edits invisible to original-source tools.

## Important APIs, Types, and Functions
`Tool` registers `patch-diff`. `state` supplies `KernelScratchSrc`; `args.File` optionally restricts output; `result.Output` holds diff text. `patchDiff` runs `git diff HEAD --function-context -U10`.

## Control Flow
It validates `KernelScratchSrc`, appends `-- <file>` when requested, runs git in the scratch repo, maps outside-repository and timeout failures to bad-call errors, and returns raw diff output.

## State and Persistence Behavior
Read-only over the scratch git worktree. It reports uncommitted state but does not mutate it.

## Dependencies and Integration Points
Depends on `aflow` and `osutil`. Integrated with `codeeditor` in patch-generation workflows.

## Risks and Test Signals
Risk is large diff output with no explicit truncation. Tests cover expanded-context diff, file restriction, nonexistent file empty output, and path escape failure.
