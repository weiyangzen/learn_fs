# sources/object-store/minio-mc/cmd/admin-rebalance-main.go

## Purpose
Defines the `mc admin rebalance` command group for starting, stopping, and inspecting MinIO rebalance operations.

## Important APIs, types, and functions
`adminRebalanceSubcommands` registers start, status, and stop. `adminRebalanceCmd` declares the group. `mainAdminRebalance` delegates invalid invocations to `commandNotFound`.

## Control flow
No rebalance API is called directly here. The file provides command routing and common global setup.

## State and persistence behavior
No state is read or mutated in this file; rebalance state lives on the server and is handled by subcommands.

## Dependencies and integration points
It depends on `minio/cli`, global flags, sibling rebalance command variables, and top-level admin registration.

## Risks and edge cases
Manual registry drift can make lifecycle operations unreachable. The group hides the help command, so shared not-found output is important.

## Test signals
Tests should verify start/status/stop registration and common behavior for bare or unknown `mc admin rebalance` invocations.
