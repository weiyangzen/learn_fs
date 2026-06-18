# sources/test-tools/syzkaller/pkg/aflow/flow/patching/actions.go

## Purpose

`actions.go` contains helper actions for patching workflows: base commit selection, maintainer discovery, recent commit summaries, applying previous patches, and forwarding patch diffs.

## Important APIs, Types, and Functions

Actions are `baseCommitPicker`, `getMaintainers`, `getRecentCommits`, `applyGitPatch`, and `forwardPatchDiff`. `pickBaseCommit` resolves `HEAD`, `RC`, or exact commits. `maintainers` runs Linux `scripts/get_maintainer.pl`. `recentCommits` parses modified files from a diff and runs `git log`. `applyGitPatchFunc` applies the latest patch history diff to a scratch tree.

## Control Flow

Base commit selection uses `kernel.UseLinuxRepo` to checkout branch, fetch tags for `RC`, resolve a release tag or exact commit, and output normalized repo/branch/commit. Maintainer lookup switches the shared repo to the target commit, pipes the patch diff to `get_maintainer.pl`, and converts parsed recipients into `ai.Recipient`s. Recent commits extracts file names from the patch diff and runs a non-merge log from the target commit over those files. Patch application validates non-empty history and runs `git apply` on the latest diff when present.

## State and Persistence Behavior

These actions mutate the shared Linux repo checkout via `UseLinuxRepo` or mutate a scratch source tree for patch application. Outputs are transient workflow state. No aflow cache is created directly here, but `UseLinuxRepo` uses the workflow workdir.

## Dependencies and Integration Points

They depend on kernel checkout helpers, syzkaller `vcs`, `osutil`, `ai` schemas, and external git/get_maintainer scripts. Patching and patch-iteration workflows use them around LLM patch generation.

## Risks and Edge Cases

The shared repo mutex is process-local. `RC` resolution depends on tag fetches and release-tag logic. `recentCommits` returns a flow error for empty diffs. `get_maintainer.pl` requires a non-shallow checkout. Applying previous patches assumes the scratch tree matches the base of the latest patch.

## Test Signals

`actions_test.go` covers `recentCommits` against the syzkaller repo when not running in shallow CI. Other actions need integration tests with a Linux repo.
