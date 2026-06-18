# sources/test-tools/syzkaller/pkg/aflow/flow/patching/actions_test.go

## Purpose

`actions_test.go` validates recent commit extraction for modified files in a patch diff.

## Important APIs, Types, and Functions

`TestRecentCommits` uses `aflow.TestAction` to run `getRecentCommits` with `recentCommitsArgs` and compare `recentCommitsResult`.

## Control Flow

The test skips on CI because shallow checkouts may not contain the reference commit. Locally, it creates a temp workdir, symlinks the repository into `repo/linux` to satisfy `kernel.UseLinuxRepo`, supplies a diff touching two files, and expects a fixed list of recent non-merge subjects.

## State and Persistence Behavior

It creates temp dirs and a symlink but no persistent repository changes. It reads the current local git history.

## Dependencies and Integration Points

It depends on `osutil`, aflow test harness, and the local repository containing the expected history.

## Risks and Edge Cases

The test is intentionally environment-sensitive and skipped in CI. Expected commit subjects can become stale if repository history is rewritten, though syzkaller history should be stable.

## Test Signals

It provides a targeted signal that `vcs.ParseGitDiff` file extraction and `git log` invocation work in the expected workdir layout.
