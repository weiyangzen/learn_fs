# sources/object-store/minio-mc/cmd/admin-replicate.go

## Purpose
Defines the `mc admin replicate` command group for MinIO site replication administration.

## Important APIs, types, and functions
`adminReplicateSubcommands` registers add, update, remove, info, status, and resync. `adminReplicateCmd` declares the group. `mainAdminReplicate` delegates invalid invocations to `commandNotFound`.

## Control flow
The file routes recognized replication lifecycle commands and has no direct server interaction.

## State and persistence behavior
No state is read or changed here. Replication configuration and metrics are handled by subcommands.

## Dependencies and integration points
It depends on `minio/cli`, global flags, sibling replicate command variables, and top-level admin registration.

## Risks and edge cases
Replication is a broad feature area, so missing a subcommand in this registry can hide significant functionality. Hidden aliases on child commands must still be registered correctly.

## Test signals
Tests should verify all child commands are reachable and that bare or unknown `replicate` invocations use shared not-found/help behavior.
