# sources/object-store/minio-mc/cmd/admin-scanner.go

## Purpose
Defines the `mc admin scanner` command group for scanner status and trace tooling.

## Important APIs, types, and functions
`adminScannerSubcommands` registers status/info and trace. `adminScannerCmd` declares the group. `mainAdminScanner` delegates invalid invocations to `commandNotFound`.

## Control flow
The file routes scanner subcommands and has no direct server interaction.

## State and persistence behavior
No state is read or modified here. Scanner metrics and trace streams are handled by child commands.

## Dependencies and integration points
It depends on `minio/cli`, global flags, sibling scanner command variables, and top-level admin registration.

## Risks and edge cases
Adding scanner tooling requires updating this registry. Hidden alias `info` is owned by the status command, not this group.

## Test signals
Tests should verify status/info and trace registration and shared behavior for bare or unknown `mc admin scanner` invocations.
