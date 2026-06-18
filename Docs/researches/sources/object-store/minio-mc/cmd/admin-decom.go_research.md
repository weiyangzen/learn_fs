# sources/object-store/minio-mc/cmd/admin-decom.go

## Purpose
Defines the `mc admin decommission` command group and its `decom` alias. It is a router for pool decommission lifecycle subcommands.

## Important APIs, types, and functions
`adminDecommissionSubcommands` registers start, status, and cancel command values. `adminDecommissionCmd` wires the group into `minio/cli`, and `mainAdminDecommission` calls `commandNotFound`.

## Control flow
When a user invokes the group without a valid subcommand, control reaches `mainAdminDecommission`, which delegates error/help behavior to the common command dispatcher. All actual behavior is implemented in the subcommand files.

## State and persistence behavior
No local or remote state is read or written here. The file only exposes the command namespace that lets sibling subcommands mutate or inspect server-side decommission state.

## Dependencies and integration points
It depends on `github.com/minio/cli`, `setGlobalsFromContext`, `globalFlags`, and sibling command variables. It is also registered from the top-level admin command.

## Risks and edge cases
The primary risk is registration drift: missing a new lifecycle subcommand here makes it unreachable even if implemented. The group hides the help command, so `commandNotFound` behavior is important for user feedback.

## Test signals
CLI registration tests should verify `decommission`, `decom`, and the start/status/cancel subcommands are reachable and that an unknown subcommand produces the shared not-found/help path.
