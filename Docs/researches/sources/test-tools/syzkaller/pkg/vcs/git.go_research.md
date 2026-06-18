# sources/test-tools/syzkaller/pkg/vcs/git.go

## Purpose

`git.go` is the core Git-backed implementation of syzkaller's `Repo` operations. It handles cloning, polling, checkout, commit metadata parsing, bisection, patch-base discovery, local command execution, and diff parsing.

## Important APIs, Types, And Functions

`gitRepo` wraps `*Git`. `newGitRepo` sets sandboxing, filtered environment, ignored CC map, and repo options. High-level methods include `Poll`, `CheckoutBranch`, `CheckoutCommit`, `FetchTags`, `SwitchCommit`, `Contains`, `GetCommitByTitle`, `GetCommitsByTitles`, `LatestCommits`, `ExtractFixTagsFromCommits`, `Bisect`, `ReleaseTag`, `Object`, `MergeBases`, `CommitExists`, `PushCommit`, and `fetchRemote`. `Git` exposes `Run`, `Apply`, `Reset`, `Commit`, `fetchCommits`, `BaseForDiff`, `BranchesThatContain`, `ContainedIn`, and `Diff`. `ParseGitDiff` extracts changed files and left blob hashes.

## Control Flow, State, Dependencies, And Integration

The implementation persists state in a checkout directory and mutates remotes, tags, branches, worktrees, submodules, and bisect state. It filters Git-related environment variables to avoid acting on the caller's repo. Non-precious repos can be removed and reinitialized on corruption; precious repos skip destructive reset. Most operations shell out with timeouts through `osutil`, optionally sandboxed.

## Risks And Test Signals

Risks include destructive cleanup for non-precious repos, command timeout dependence, shallow assumptions about Git error codes, regex-based metadata parsing, long-running `BaseForDiff`, and non-coalesced remote naming via URL hash. Tests in `git_repo_test.go` and `git_test.go` cover checkout flows, local commit reuse, metadata, bisection, tags, custom refs, short hashes, diff parsing, object extraction, merge bases, file hashes, and patch-base minimization.
