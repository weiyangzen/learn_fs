# sources/object-store/minio-mc/cmd/admin-replicate-resync.go

## Purpose
Defines the `mc admin replicate resync` subcommand group for starting, checking, and canceling site resync operations.

## Important APIs, types, and functions
`adminReplicateResyncSubcommands` registers start, status, and cancel. `adminReplicateResyncCmd` declares the group. `mainAdminReplicateResync` delegates invalid invocations to `commandNotFound`.

## Control flow
The file performs only routing. Recognized subcommands execute their own source/peer alias logic.

## State and persistence behavior
No state is read or changed in this file. Resync jobs are server-side state managed by child commands.

## Dependencies and integration points
It depends on `minio/cli`, global flags, sibling resync command variables, and the parent replicate command group.

## Risks and edge cases
Registration drift could make a resync lifecycle action unreachable. Bare group invocation depends on shared not-found/help output.

## Test signals
Tests should verify start/status/cancel registration and shared behavior for bare or unknown resync subcommands.
