# sources/object-store/minio-mc/cmd/admin-rebalance-stop.go

## Purpose
Implements `mc admin rebalance stop`, stopping an ongoing MinIO rebalance operation.

## Important APIs, types, and functions
`adminRebalanceStopCmd` defines the command. `rebalanceStopMsg` handles JSON and human success messages. `mainAdminRebalanceStop` calls `RebalanceStop`.

## Control flow
The handler validates exactly one alias, creates an admin client, invokes the stop API, and prints a target-specific success message.

## State and persistence behavior
The persistent mutation is server-side transition of rebalance state toward stopped/canceled. No local state is stored.

## Dependencies and integration points
It depends on MinIO admin rebalance APIs, global context, console color setup, `colorjson`, and `probe` error wrapping.

## Risks and edge cases
Stopping when no rebalance is active is left to server error semantics. Human output does not include a rebalance ID.

## Test signals
Tests should cover arity validation, client failure, stop API failure, JSON status/target output, and human success output.
