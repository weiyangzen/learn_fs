# sources/object-store/minio-mc/cmd/admin-policy.go

## Purpose
Defines the `mc admin policy` command group for managing MinIO server IAM policies and their associations.

## Important APIs, types, and functions
`adminPolicySubcommands` registers create, remove, list, info, attach, detach, entities, and deprecated add/set/unset/update entries. `adminPolicyCmd` defines the group. `mainAdminPolicy` delegates to `commandNotFound`.

## Control flow
The file routes recognized policy subcommands. Bare or invalid invocations enter the shared command-not-found path.

## State and persistence behavior
No state is accessed here. Policy creation, removal, association, and queries happen in subcommand files.

## Dependencies and integration points
It depends on `minio/cli`, global flags, sibling command variables, and the top-level admin command registry.

## Risks and edge cases
Manual subcommand registration can drift from implemented files. Deprecated commands remain present but hidden, which affects command discovery and compatibility.

## Test signals
Tests should verify active and deprecated policy subcommands are registered, aliases work where defined, and bare `mc admin policy` uses common not-found/help behavior.
