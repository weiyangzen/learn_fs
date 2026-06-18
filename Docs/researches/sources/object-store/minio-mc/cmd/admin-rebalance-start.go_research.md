# sources/object-store/minio-mc/cmd/admin-rebalance-start.go

## Purpose
Implements `mc admin rebalance start`, initiating a MinIO rebalance operation for a deployment.

## Important APIs, types, and functions
`adminRebalanceStartCmd` defines the command. `rebalanceStartMsg` serializes success output. `mainAdminRebalanceStart` calls `RebalanceStart`.

## Control flow
The handler requires exactly one alias, creates an admin client, starts rebalance through the server API, and prints a success message containing the target and returned rebalance ID.

## State and persistence behavior
The persistent state change is server-side creation/start of a rebalance operation. The returned ID is only displayed locally.

## Dependencies and integration points
It integrates `madmin-go` rebalance APIs, global context, console colors, `probe` errors, and global JSON output.

## Risks and edge cases
The help template contains `xEXAMPLES`, likely a typo. The human message does not include the rebalance ID, while JSON does. Existing rebalance conflicts are handled only by the server.

## Test signals
Tests should cover single-argument validation, client initialization failure, server start error, JSON ID output, and human success rendering.
