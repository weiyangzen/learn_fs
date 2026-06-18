<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/deletefile/deletefile.go -->
# sources/user-network-fs/rclone/cmd/deletefile/deletefile.go

## Purpose

`deletefile.go` implements `rclone deletefile`, removing exactly one remote object without filter processing and without deleting directories.

## Important APIs, Types, and Functions

The command validates one path, resolves it with `cmd.NewFsFile`, requires a non-empty file name, gets the object with `f.NewObject`, and calls `operations.DeleteFile`.

## Control Flow

It runs under `cmd.Run(true, false, ...)`. Directory or nonexistent paths that resolve without a file name return an `fs.ErrorObjectNotFound`-wrapped error.

## State and Persistence Behavior

It deletes one remote object. No local persistent state is created.

## Dependencies and Integration Points

It uses `cmd.NewFsFile`, backend `NewObject`, `operations.DeleteFile`, and standard retry behavior.

## Risks and Test Signals

Risks include ambiguous nonexistent vs directory errors, retrying deletes after a first successful attempt, bypassing filters unexpectedly, and backend object lookup quirks. Tests should cover existing object deletion, directory rejection, missing object, dry-run/interactive lower-layer behavior, and retry classification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/deletefile/deletefile.go -->
