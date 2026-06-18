# sources/object-store/minio-mc/cmd/admin-replicate-resync-cancel.go

## Purpose
Implements `mc admin replicate resync cancel`, canceling an ongoing resync operation from one replicated site to another.

## Important APIs, types, and functions
`adminReplicateResyncCancelCmd` defines the command. `resyncCancelMessage` wraps `madmin.SRResyncOpStatus`. `mainAdminReplicateResyncCancel` calls `SiteReplicationInfo`, peer `ServerInfo`, and `SiteReplicationResyncOp` with `SiteResyncCancel`.

## Control flow
The command requires source and peer aliases. It fetches replication info from the source, gets the peer deployment ID through `getClient(...).ServerInfo`, matches that ID to a configured peer, rejects non-members, sends the cancel operation, and prints success or error detail.

## State and persistence behavior
The persistent state change is server-side cancellation of a resync identified by the peer deployment. Local state is transient peer lookup data.

## Dependencies and integration points
It integrates site replication metadata, peer client/server info APIs, resync operation constants, global context, and shared console/JSON output.

## Risks and edge cases
Peer matching depends on deployment IDs rather than alias names. If the peer is unreachable, cancellation cannot proceed. The `ResyncErr` color is not set in this file, unlike start.

## Test signals
Tests should cover arity validation, peer deployment matching, non-member rejection, source or peer API failures, cancel operation payload, success message with resync ID, and error-detail output.
