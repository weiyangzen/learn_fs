<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cleanup/cleanup.go -->
# sources/user-network-fs/rclone/cmd/cleanup/cleanup.go

## Purpose

`cleanup.go` implements `rclone cleanup`, invoking a backend-specific cleanup operation such as emptying trash or deleting old versions.

## Important APIs, Types, and Functions

The command is registered in `init`. Its Cobra `Run` validates one remote argument, resolves it with `cmd.NewFsSrc`, and calls `operations.CleanUp` inside `cmd.Run(true, false, ...)`.

## Control Flow

The command uses the standard retry loop because cleanup can fail transiently. The actual behavior is entirely backend feature dependent.

## State and Persistence Behavior

This command can mutate remote-side storage, trash, or version history. It creates no local persistent state.

## Dependencies and Integration Points

It integrates with rclone's operation layer and any backend implementing cleanup semantics.

## Risks and Test Signals

Risks are backend-specific data loss, unsupported backend errors, dry-run expectations not being obvious, and retrying non-idempotent cleanup. Tests should cover unsupported remotes, a mock cleanup feature, retry classification, and preservation of normal command exit behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cleanup/cleanup.go -->
