# sources/object-store/minio-mc/cmd/admin-group-info.go

## Purpose
Implements `mc admin group info`, displaying members, policy, and status for a MinIO IAM group.

## Important APIs, types, and functions
The key symbols are `adminGroupInfoCmd`, `checkAdminGroupInfoSyntax`, and `mainAdminGroupInfo`. The handler calls `GetGroupDescription` and prints `groupMessage` with `GroupStatus`, `GroupPolicy`, and `Members`.

## Control flow
The command requires exactly target and group name. It creates an admin client, fetches the group description from the server, then delegates human or JSON rendering to the shared group message type.

## State and persistence behavior
No state is changed. The command reads persistent group metadata from MinIO IAM configuration and exposes it to the terminal or JSON stream.

## Dependencies and integration points
It uses the shared admin client, global context, `probe` error tracing, console color setup, and the message formatter declared in the add command file.

## Risks and edge cases
Large member lists are printed as a single comma-separated line in human output, which can be hard to read. Policy is displayed as returned by the server; missing policy or disabled state is not specially annotated beyond the raw fields.

## Test signals
Tests should cover argument validation, successful mapping from `GetGroupDescription` to output fields, JSON field names, and failures for nonexistent groups or admin API errors.
