# sources/object-store/minio-mc/cmd/admin-replicate-update.go

## Purpose
Implements `mc admin replicate update`/`edit`, modifying site replication peer endpoint, sync mode, bucket bandwidth defaults, or ILM expiry replication behavior.

## Important APIs, types, and functions
`adminReplicateUpdateFlags` defines deployment, endpoint, mode/sync, bandwidth, and ILM expiry toggles. `updateSuccessMessage` wraps `madmin.ReplicateEditStatus`. `checkAdminReplicateUpdateSyntax` and `mainAdminReplicateUpdate` perform validation and call `SiteReplicationEdit`.

## Control flow
The handler requires one alias, creates an admin client, enforces required flag combinations, rejects conflicting mode/sync or ILM toggles, parses deprecated `--sync` or modern `--mode`, parses bandwidth with `getBandwidthInBytes`, validates endpoint URL, builds `madmin.PeerInfo` plus `SREditOptions`, calls the server, and prints status.

## State and persistence behavior
The persistent mutation is server-side site replication peer metadata or global ILM expiry replication setting. Local state is transient parsed flags.

## Dependencies and integration points
It integrates URL parsing, bandwidth parsing helpers, MinIO site replication edit APIs, sync-state constants, global context, colorized output, and JSON serialization.

## Risks and edge cases
ILM expiry toggles must not be combined with deployment ID. Deprecated `--sync` remains hidden for compatibility. URL parsing accepts syntactically valid but semantically unusable endpoints; deeper validation is server-side.

## Test signals
Tests should cover required flag validation, conflict validation, sync/mode mapping, bandwidth parsing failures, endpoint parsing, ILM-only updates, deployment-specific updates, server errors, and output with `ErrDetail`.
