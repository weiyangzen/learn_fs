# sources/object-store/minio-mc/cmd/admin-group.go

## Purpose
Defines the `mc admin group` command namespace for MinIO IAM group management.

## Important APIs, types, and functions
`adminGroupSubcommands` registers add, remove, info, list, enable, and disable. `adminGroupCmd` is the CLI group definition, and `mainAdminGroup` delegates unmatched invocation to `commandNotFound`.

## Control flow
The file performs no group operation directly. It is entered only when no registered subcommand handles the invocation, at which point the common command-not-found path displays the relevant guidance.

## State and persistence behavior
No local or server state is accessed here. State changes are owned by subcommand handlers.

## Dependencies and integration points
It depends on the `cli` package, global flags, command initialization, and sibling command variables. The top-level admin command imports this command group.

## Risks and edge cases
Adding a new group subcommand requires updating this list. Hidden help behavior means registration and `commandNotFound` output are the main user-facing contract.

## Test signals
Tests should verify all group subcommands and aliases are reachable under `mc admin group` and that bare or invalid invocations route to the shared not-found behavior.
