# sources/object-store/minio-mc/cmd/admin-rebalance-status.go

## Purpose
Implements `mc admin rebalance status`, summarizing per-pool and aggregate progress for an ongoing rebalance.

## Important APIs, types, and functions
`adminRebalanceStatusCmd` defines the command. `mainAdminRebalanceStatus` calls `RebalanceStatus`, uses `console.NewTable`, `humanize.IBytes`, and aggregates progress fields.

## Control flow
The handler validates a single alias, creates an admin client, fetches rebalance info, returns raw JSON when requested, otherwise renders a per-pool usage table. It marks pools with status `Started`, sums bytes/objects/versions, tracks maximum elapsed and ETA, and prints a summary.

## State and persistence behavior
The command is read-only. It observes server-side rebalance progress and does not persist local state.

## Dependencies and integration points
It integrates admin rebalance status APIs, standard `encoding/json` for raw JSON, console tables/colors, humanized byte formatting, and global context.

## Risks and edge cases
Column headers are zero-based (`Pool-0`) while other commands often display one-based pool ordinals. Empty pool lists produce empty table inputs. Summary ETA chooses the maximum ETA across pools.

## Test signals
Tests should cover JSON output, per-pool table output, started marker, aggregate totals, max elapsed/ETA selection, client initialization errors, and empty or completed rebalance states.
