# sources/object-store/minio-mc/cmd/admin-user-disable.go

## Purpose

`admin-user-disable.go` implements `mc admin user disable`, changing a MinIO user account status to disabled.

## Important APIs, Types, and Functions

`adminUserDisableCmd` declares the command. `checkAdminUserDisableSyntax` enforces target and username. `mainAdminUserDisable` calls `SetUserStatus` with `madmin.AccountDisabled`.

## Control Flow

The handler validates two args, creates an admin client for the target, sends the status update for the username, and prints a `userMessage` with operation `disable`.

## State and Persistence Behavior

Remote IAM account status is persisted by the server. The client writes no local files.

## Dependencies and Integration Points

It uses the shared `userMessage` type from `admin-user-add.go`, `newAdminClient`, `madmin-go`, `fatalIf`, and global flags.

## Risks and Edge Cases

The command has no confirmation, so accidental disables take effect immediately. It does not inspect the previous status.

## Test Signals

Tests should verify arity, status value `AccountDisabled`, error propagation, and output message content.
