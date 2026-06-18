# sources/test-tools/syzkaller/pkg/vcs/linux_patches_test.go

## Purpose

This file tests the generic backport helper used by Linux bisection.

## Important APIs, Types, And Functions

`TestFixBackport` creates a fix on a separate branch and verifies `BackportCommits` cherry-picks it into `main`. `TestConditionalFixBackport` creates branches with and without the guilty commit and verifies conditional application based on `GuiltyHash`.

## Control Flow, State, Dependencies, And Integration

Tests use temp Git repos, real file writes, real branch switching, and `osutil.IsExist` to validate worktree effects. They pass an empty remote URL because all commits are local.

## Risks And Test Signals

The tests catch accidental unconditional application of conditional fixes and failure to cherry-pick local fix commits. They do not test duplicate-title skip behavior, remote fetching, conflict handling, or built-in Linux backport list freshness.
