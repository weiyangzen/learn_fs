# sources/object-store/minio-mc/cmd/admin-user-remove.go

## Purpose

`admin-user-remove.go` implements `mc admin user remove` / `rm`, deleting a user from MinIO IAM.

## Important APIs, Types, and Functions

`adminUserRemoveCmd` declares the command and short name. `checkAdminUserRemoveSyntax` enforces target and username. `mainAdminUserRemove` calls `RemoveUser`.

## Control Flow

The handler validates two args, creates an admin client, sends the remove request for the username, and prints a shared `userMessage`.

## State and Persistence Behavior

Remote IAM user state is deleted by the server. No local state is persisted.

## Dependencies and Integration Points

It uses `newAdminClient`, `madmin.AdminClient.RemoveUser`, shared user output, global context, and error helpers.

## Risks and Edge Cases

The command has no confirmation and no dependency check for policies or service accounts; server-side validation determines deletion behavior.

## Test Signals

Tests should assert exact arity, target/user propagation, error path, and remove message rendering.
