# sources/test-tools/syzkaller/pkg/testutil/norace.go

## Purpose

`norace.go` provides the `RaceEnabled` build-time constant for normal, non-race builds.

## Important APIs, Types, And Functions

Under build tag `!race`, it defines `const RaceEnabled = false` in package `testutil`.

## Control Flow, State, Dependencies, And Integration

There is no runtime control flow or state. The file complements `race.go`; exactly one is selected by Go build tags. `testutil.IterCount` uses this constant to scale randomized test iteration counts.

## Risks And Test Signals

The risk is accidental build-tag mismatch causing duplicate or missing constants. Behavior is implicitly covered wherever `testutil.IterCount` is used in race and non-race builds.
