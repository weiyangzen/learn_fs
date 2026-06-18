# sources/test-tools/syzkaller/pkg/vcs/linux_patches.go

## Purpose

`linux_patches.go` defines conditional backport rules for Linux bisection and the generic helper that cherry-picks needed fix commits.

## Important APIs, Types, And Functions

`BackportCommit` describes optional `GuiltyHash`, required `FixHash`, and human comment. `linuxFixBackports` applies built-in `pickLinuxCommits` plus extras from a default Linux remote. `BackportCommits` checks whether the guilty commit is present, fetches the fix if needed, detects whether a commit with the same original title is already present, and cherry-picks missing fixes. `pickLinuxCommits` lists known build/boot fixes.

## Control Flow, State, Dependencies, And Integration

The function mutates the repo worktree through `cherryPick` without committing. It uses `Contains`, `fetchRemote`, `Commit`, `GetCommitByTitle`, and title-based duplicate detection with a wider since cutoff. It returns whether any patch was applied.

## Risks And Test Signals

Cherry-pick conflicts, title collisions, missing remotes, and stale hashes can fail bisections. Title-based detection can miss retitled fixes or match unrelated commits. `linux_patches_test.go` covers unconditional and guilty-hash-conditional backport behavior.
