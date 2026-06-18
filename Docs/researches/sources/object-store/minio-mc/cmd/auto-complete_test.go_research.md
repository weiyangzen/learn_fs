# sources/object-store/minio-mc/cmd/auto-complete_test.go

## Purpose

`auto-complete_test.go` verifies that every visible leaf command has a registered completion predictor in `completeCmds`.

## Important APIs, Types, and Functions

The single test `TestAutoCompletionCompletness` recursively walks `appCmds` and checks `completeCmds` for visible commands without subcommands.

## Control Flow

The nested `checkCompletion` function skips hidden command branches, recurses into subcommands, and fails when a visible leaf command path is missing from `completeCmds`.

## State and Persistence Behavior

There is no persistence. The test reads the static command tree and completion map.

## Dependencies and Integration Points

It depends on `appCmds`, `cli.Command`, and the path naming convention used by `cmdToCompleteCmd`.

## Risks and Edge Cases

The check uses `if cmd.Hidden` inside the subcommand loop instead of checking `subCmd.Hidden`, so hidden child behavior relies partly on recursive logic. It only checks presence, not correctness of predictors.

## Test Signals

The primary signal is failure naming the missing command path. Additional tests could validate predictor behavior for representative commands.
