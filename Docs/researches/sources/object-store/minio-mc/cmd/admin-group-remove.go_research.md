# sources/object-store/minio-mc/cmd/admin-group-remove.go

## Purpose
Implements `mc admin group remove`/`rm`, removing members from a group or deleting the group when no member names are provided.

## Important APIs, types, and functions
`adminGroupRemoveCmd` defines the command. `checkAdminGroupRemoveSyntax` requires target and group. `mainAdminGroupRemove` builds `madmin.GroupAddRemove{IsRemove: true}` and calls `UpdateGroupMembers`.

## Control flow
After validation and client creation, the handler collects optional member arguments. It sends the group name and member slice to the server as a remove operation, then prints a message that distinguishes member removal from whole-group removal based on whether the member slice is empty.

## State and persistence behavior
Server-side IAM group state is mutated: either membership is changed or the group is removed. The local process keeps only a transient member list for output.

## Dependencies and integration points
It shares the add/remove server API with `admin-group-add.go`, the message renderer, color setup, `probe` errors, and global context.

## Risks and edge cases
Deleting a group is represented by an empty member list, so accidental omission of members changes the operation's impact. Local code does not prompt for confirmation or validate group membership; server-side checks are relied on.

## Test signals
Tests should cover member-removal payloads, empty-member group deletion payloads, short-name registration, server error handling, and the two human output variants.
