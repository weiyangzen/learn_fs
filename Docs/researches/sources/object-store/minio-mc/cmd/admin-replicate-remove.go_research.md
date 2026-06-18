# sources/object-store/minio-mc/cmd/admin-replicate-remove.go

## Purpose
Implements `mc admin replicate remove`/`rm`, removing selected sites or all sites from site replication configuration.

## Important APIs, types, and functions
`adminReplicateRemoveFlags` defines `--all` and `--force`. `srRemoveStatus` wraps `madmin.ReplicateRemoveStatus`. `checkAdminReplicateRemoveSyntax` enforces dangerous-operation constraints. `mainAdminReplicationRemoveStatus` calls `SiteReplicationRemove`.

## Control flow
The syntax checker rejects `--all` with extra site args, requires sites unless `--all`, and requires `--force` for all removals. The handler builds `madmin.SRRemoveReq`, calls the server, and prints a full, partial, or all-sites success message.

## State and persistence behavior
The persistent mutation is removal of site replication configuration from the active cluster or all participating sites, depending on request flags.

## Dependencies and integration points
It integrates MinIO site replication removal APIs, global context, colorized output, JSON serialization, and CLI dangerous-operation safeguards.

## Risks and edge cases
The operation is irreversible and only protected by `--force`; there is no interactive prompt. Partial failures are reported through status detail and must be surfaced to users.

## Test signals
Tests should cover `--force` requirement, `--all` exclusivity, site list requirements, payload construction, full and partial response messages, JSON output, and server failure propagation.
