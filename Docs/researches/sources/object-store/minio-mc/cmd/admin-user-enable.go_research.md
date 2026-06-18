# sources/object-store/minio-mc/cmd/admin-user-enable.go

## Purpose

`admin-user-enable.go` implements `mc admin user enable`, changing a MinIO user account status to enabled.

## Important APIs, Types, and Functions

`adminUserEnableCmd` declares the command. `checkAdminUserEnableSyntax` enforces target and username. `mainAdminUserEnable` calls `SetUserStatus` with `madmin.AccountEnabled`.

## Control Flow

The handler validates two args, creates an admin client, updates the user status, and prints a shared user success message.

## State and Persistence Behavior

The server persists the enabled account status. No local files are touched.

## Dependencies and Integration Points

It integrates with the admin user command group, shared `userMessage`, `madmin-go`, and common error/output helpers.

## Risks and Edge Cases

There is no prior-state check or confirmation. Enabling an externally managed account may depend on server-side IAM behavior.

## Test Signals

Tests should assert syntax, `AccountEnabled` propagation, and output for successful enablement.
