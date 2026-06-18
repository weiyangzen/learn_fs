# sources/object-store/minio-mc/cmd/admin-replicate-resync-start.go

## Purpose
Implements `mc admin replicate resync start`, starting a bucket-data resync toward a peer site.

## Important APIs, types, and functions
`adminReplicateResyncStartCmd` defines the command. `resyncMessage` wraps `madmin.SRResyncOpStatus`. `mainAdminReplicateResyncStart` uses `SiteReplicationInfo`, peer `ServerInfo`, and `SiteReplicationResyncOp` with `SiteResyncStart`.

## Control flow
The command requires source and peer aliases. It opens the source admin client, fetches configured sites, obtains peer deployment ID from the peer alias, finds the matching `PeerInfo`, rejects aliases outside replication, starts resync, and prints the returned resync ID or error detail.

## State and persistence behavior
The persistent effect is a server-side resync job for the selected peer deployment. Local state is limited to lookup and output.

## Dependencies and integration points
It integrates source and peer admin clients, site replication info, resync operation constants, global context, and colorized/JSON status output.

## Risks and edge cases
Alias names are not trusted; deployment ID matching is authoritative. Unreachable peer aliases prevent lookup. The command does not accept bucket filters; resync scope is determined by server API semantics.

## Test signals
Tests should cover exactly two arguments, peer matching, non-member failure, resync start API errors, returned resync ID output, and error-detail rendering.
