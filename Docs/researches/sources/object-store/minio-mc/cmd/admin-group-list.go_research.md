# sources/object-store/minio-mc/cmd/admin-group-list.go

## Purpose
Implements `mc admin group list` and its `ls` short name, listing all MinIO IAM groups for an alias.

## Important APIs, types, and functions
`adminGroupListCmd` defines command metadata. `checkAdminGroupListSyntax` requires one target. `mainAdminGroupList` calls `ListGroups` and prints a `groupMessage` with `op: list`.

## Control flow
The handler validates the single alias argument, creates an admin client, fetches group names, and sends them to the shared renderer. Human output prints one colorized group per line; JSON output includes the `groups` array.

## State and persistence behavior
This is read-only. It observes server IAM group names and writes no local state.

## Dependencies and integration points
It depends on MinIO admin IAM APIs, the global CLI/output plumbing, console colors, and shared group message serialization.

## Risks and edge cases
The command does not sort locally, so output order follows server behavior. Empty group lists render as an empty string in human output, which may be ambiguous.

## Test signals
Tests should check syntax, alias client creation, API error propagation, empty and multi-group output, short-name registration, and JSON array rendering.
