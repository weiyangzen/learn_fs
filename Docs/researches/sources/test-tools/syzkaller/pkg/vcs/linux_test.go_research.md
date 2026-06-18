# sources/test-tools/syzkaller/pkg/vcs/linux_test.go

## Purpose

`linux_test.go` tests Linux compiler selection rules used for bisection environments.

## Important APIs, Types, And Functions

`TestClangVersion` checks `linuxClangPath` with no tags, `v5.9`, and `v6.15`. `TestGCCVersion` checks `linuxGCCPath` with no tags, `v4.12`, and `v5.16`.

## Control Flow, State, Dependencies, And Integration

Tests use a simple tag map and expected path strings built from a fake binary directory or default compiler path. There is no filesystem access.

## Risks And Test Signals

These tests protect bisection compiler compatibility cutoffs. They are intentionally tied to hard-coded historical rules, so adding new compiler thresholds requires test updates. They do not cover `PreviousReleaseTags` cutoff filtering or `EnvForCommit` as a whole.
