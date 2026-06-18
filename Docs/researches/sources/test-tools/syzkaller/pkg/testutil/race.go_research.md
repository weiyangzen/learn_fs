# sources/test-tools/syzkaller/pkg/testutil/race.go

## Purpose

`race.go` provides the `RaceEnabled` build-time constant for race-detector builds.

## Important APIs, Types, And Functions

Under build tag `race`, it defines `const RaceEnabled = true` in package `testutil`.

## Control Flow, State, Dependencies, And Integration

There is no runtime control flow or state. It is selected by Go's race build tag and influences `IterCount`, allowing expensive randomized tests to run fewer iterations under the slower race detector.

## Risks And Test Signals

The file is small but important for keeping test suites practical under `go test -race`. Build-tag correctness is the main risk and is validated by compilation under race builds.
