# sources/object-store/minio-mc/cmd/cli_test.go

## Purpose

`cli_test.go` verifies that visible leaf commands define `OnUsageError`, ensuring consistent usage-error handling across the CLI.

## Important APIs, Types, and Functions

`TestCLIOnUsageError` recursively walks `appCmds` and checks `cli.Command.OnUsageError` for visible leaves.

## Control Flow

The nested `checkOnUsageError` recurses into subcommands, skips hidden command branches, and records an error when a visible leaf command lacks usage-error handling.

## State and Persistence Behavior

No persistence; it inspects static CLI metadata.

## Dependencies and Integration Points

It depends on `appCmds`, `cli.Command`, and the convention that user-invokable leaf commands should set `OnUsageError`.

## Risks and Edge Cases

Like the autocomplete test, the hidden-check inside the loop checks the parent command rather than the child before recursion. It only validates presence, not behavior of the handler.

## Test Signals

The signal is a test failure naming the command path missing `OnUsageError`.
