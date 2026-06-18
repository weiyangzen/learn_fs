# sources/object-store/minio-mc/cmd/admin-user-add.go

## Purpose

`admin-user-add.go` implements `mc admin user add` and defines shared user output types used by other user subcommands.

## Important APIs, Types, and Functions

`adminUserAddCmd` defines the command. `userGroup` and `userMessage` model user display and JSON output across add/list/info/remove/enable/disable. `fetchUserKeys` obtains credentials from args, terminal prompts, hidden password input, or piped stdin. `mainAdminUserAdd` calls `AddUser`.

## Control Flow

The handler accepts target plus optional access and secret keys. If keys are missing, `fetchUserKeys` prompts or reads stdin based on terminal detection. The handler creates an admin client, calls `client.AddUser(globalContext, accessKey, secretKey)`, and prints an enabled user message.

## State and Persistence Behavior

Local state is not persisted. Remote IAM user state is created on the MinIO server. In JSON mode the `SecretKey` field may be emitted, so output handling is sensitive.

## Dependencies and Integration Points

It depends on `madmin` through the admin client, terminal password reading from `x/term`, shared console helpers, and user message rendering used by sibling user files.

## Risks and Edge Cases

Credentials passed as command-line args can leak into shell history; the help warns about this. `fetchUserKeys` ignores read errors from `ReadLine` and `ReadPassword`. JSON output includes secrets after add.

## Test Signals

Tests should cover one-, two-, and three-argument credential input, terminal and piped stdin paths, invalid arity, `AddUser` arguments, and text/JSON rendering for user messages.
