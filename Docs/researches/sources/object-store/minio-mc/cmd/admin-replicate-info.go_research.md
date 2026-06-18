# sources/object-store/minio-mc/cmd/admin-replicate-info.go

## Purpose
Implements `mc admin replicate info`, displaying cluster-level site replication configuration and peer details.

## Important APIs, types, and functions
`adminReplicateInfoCmd` declares the command. `srInfo` wraps `madmin.SiteReplicationInfo` and renders JSON or a table of deployment ID, site name, endpoint, sync state, bandwidth, and ILM expiry replication.

## Control flow
The handler requires exactly one alias, configures table colors, creates an admin client, calls `SiteReplicationInfo`, and prints `srInfo`. Human output shows a disabled message or a two-line header plus one row per peer.

## State and persistence behavior
This command is read-only. It observes site replication metadata stored by the server.

## Dependencies and integration points
It integrates MinIO site replication APIs, pretty-table helpers from the command package, humanized bandwidth formatting, sync-state constants, and global JSON mode.

## Risks and edge cases
The endpoint column uses fixed widths and can truncate or misalign long URLs. A zero bandwidth limit is shown as `N/A`, which means no cluster bandwidth configured rather than unknown.

## Test signals
Tests should cover enabled and disabled replication, peer row formatting, sync check marker, bandwidth formatting, ILM expiry boolean output, JSON serialization, and arity validation.
