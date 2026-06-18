# sources/object-store/minio-mc/cmd/admin-user-info.go

## Purpose

`admin-user-info.go` implements `mc admin user info`, displaying a user's status, policies, group membership, and authentication source.

## Important APIs, Types, and Functions

`adminUserInfoCmd` defines the command. `mainAdminUserInfo` calls `GetUserInfo` and then `GetGroupDescription` for each group. `authInfoToUserMessage` formats `madmin.UserAuthInfo`.

## Control Flow

The handler validates target and username, creates an admin client, fetches user info, expands each group into a `userGroup` with policy list, converts authentication info, and prints a `userMessage` with operation `info`.

## State and Persistence Behavior

The command reads remote IAM state only. No local persistence occurs.

## Dependencies and Integration Points

It depends on `madmin.UserInfo`, group description APIs, shared user output formatting, console coloring, and global context.

## Risks and Edge Cases

Group expansion requires additional admin API calls; a failure fetching any group fails the whole user-info command. Group policy names are split on commas without trimming.

## Test Signals

Tests should cover users with no groups, multiple groups and policies, builtin and external auth info, group API failures, and JSON output structure.
