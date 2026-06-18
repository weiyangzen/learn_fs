# sources/object-store/minio-mc/cmd/admin-replicate-add.go

## Purpose
Implements `mc admin replicate add`, configuring cluster-level site replication across two or more MinIO aliases.

## Important APIs, types, and functions
`adminReplicateAddFlags` defines `--replicate-ilm-expiry`. `successMessage` wraps `madmin.ReplicateAddStatus`. `mainAdminReplicateAdd` builds `madmin.PeerSite` entries and calls `SiteReplicationAdd`.

## Control flow
The command requires at least two aliases. It creates an admin client for the first alias, then creates admin clients for every provided alias to extract endpoint URL and access/secret keys. It sends the peer list plus `SRAddOptions` to the first site's admin API and prints status, error detail, and initial sync messages.

## State and persistence behavior
The persistent effect is server-side site replication configuration, including credentials and optional ILM expiry replication. Local credentials are transient in memory.

## Dependencies and integration points
It integrates alias credential resolution, `madmin-go` site replication add APIs, global context, colorized user messages, and JSON serialization.

## Risks and edge cases
Every alias must be configured and accessible locally before the server call. Passing credentials from each alias is sensitive. Partial initial-sync errors can appear in a success response and must be visible.

## Test signals
Tests should cover minimum argument enforcement, peer-site payload construction, ILM expiry flag propagation, credential extraction, server error handling, and output containing `ErrDetail`/`InitialSyncErrorMessage`.
