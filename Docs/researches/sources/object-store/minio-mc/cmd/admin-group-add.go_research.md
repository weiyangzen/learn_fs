# sources/object-store/minio-mc/cmd/admin-group-add.go

## Purpose
Implements `mc admin group add`, adding members to a new or existing MinIO IAM group. It also defines the shared `groupMessage` renderer used by group add, remove, list, info, enable, and disable commands.

## Important APIs, types, and functions
The command is `adminGroupAddCmd`. `checkAdminGroupAddSyntax` requires target, group name, and at least one member. `groupMessage.String` and `JSON` format group command results. `mainAdminGroupAdd` builds `madmin.GroupAddRemove` and calls `UpdateGroupMembers`.

## Control flow
The handler validates arguments, sets the group output color, creates an admin client for the alias, collects members from argument index two onward, calls the admin API with `IsRemove: false`, and prints a success message with the group and member list.

## State and persistence behavior
The persistent mutation is server-side IAM group membership. The client writes no local files. JSON status is synthesized locally after the server accepts the membership update.

## Dependencies and integration points
The file depends on MinIO admin IAM APIs, `probe` error wrapping, global context cancellation, `printMsg`, console colorization, and `colorjson`.

## Risks and edge cases
Argument parsing does not de-duplicate members or validate user existence locally; server validation is authoritative. Human output joins members with commas without spaces. The shared renderer means changes here can alter output for multiple group commands.

## Test signals
Tests should assert syntax enforcement, correct `GroupAddRemove` payload, fatal handling for admin API failures, JSON output shape, and stable human strings for add/list/remove/info/enable/disable operations.
