# sources/test-tools/syzkaller/pkg/vcs/git_repo_test.go

## Purpose

This file integration-tests `gitRepo` behavior against synthetic local repositories.

## Important APIs, Types, And Functions

`init` disables sandboxing for tests. `TestGitRepo` exercises polling, branch checkout, commit checkout across remotes, switching commits, and `Contains`. `TestCheckoutCommitLocal` ensures a commit already present locally is reused even when a requested alternate remote lacks it. `TestMetadata` validates commit metadata and fix-tag extraction using `metadataTests`. `TestBisect` tests conclusive and inconclusive bisection outcomes.

## Control Flow, State, Dependencies, And Integration

Tests create temp Git repositories with `CreateTestRepo` and `MakeTestRepo`, then run real Git commands. They depend on local Git behavior and disable syzkaller sandboxing because test repos are not sandbox-owned.

## Risks And Test Signals

These tests catch high-value regressions in repo lifecycle and metadata parsing. They can be sensitive to Git version differences, especially bisection output order; the test sorts inconclusive results. They do not cover network failures or submodules.
