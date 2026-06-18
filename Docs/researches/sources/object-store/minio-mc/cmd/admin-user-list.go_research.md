# sources/object-store/minio-mc/cmd/admin-user-list.go

## Purpose

`admin-user-list.go` implements `mc admin user list` / `ls`, printing all users and their statuses, policies, and group memberships.

## Important APIs, Types, and Functions

`adminUserListCmd` declares the command and short name. `mainAdminUserList` calls `ListUsers` and emits a `userMessage` for each returned user. `checkAdminUserListSyntax` enforces one target.

## Control Flow

The handler configures colors, creates an admin client, fetches all users, iterates the returned map, expands each user's groups through `GetGroupDescription`, and prints per-user rows/messages.

## State and Persistence Behavior

Remote IAM state is read only. Local state is transient table/message construction.

## Dependencies and Integration Points

It uses shared user message formatting, `madmin` user/group APIs, colorized table fields, `globalContext`, and command group registration.

## Risks and Edge Cases

Map iteration order is not sorted, so output order can be nondeterministic. Fetching group descriptions per user may be expensive and can fail the whole listing.

## Test Signals

Tests should verify arity, empty user set, group policy expansion, JSON rows, and whether output ordering needs stabilization.
