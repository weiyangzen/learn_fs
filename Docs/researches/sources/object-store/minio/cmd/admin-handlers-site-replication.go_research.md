# sources/object-store/minio/cmd/admin-handlers-site-replication.go

## Purpose
`admin-handlers-site-replication.go` implements MinIO admin and internal peer endpoints for site replication. It covers joining/removing/editing peer clusters, peer-applied IAM and bucket metadata replication, status/metainfo reporting, resync control, and network performance/dev-null utilities used by site-replication diagnostics.

## Important APIs, Types, And Functions
External admin handlers include `SiteReplicationAdd`, `SiteReplicationInfo`, `SiteReplicationStatus`, `SiteReplicationMetaInfo`, `SiteReplicationEdit`, `SiteReplicationRemove`, `SiteReplicationResyncOp`, `SiteReplicationDevNull`, and `SiteReplicationNetPerf`.

Internal peer handlers include `SRPeerJoin`, `SRPeerBucketOps`, `SRPeerReplicateIAMItem`, `SRPeerReplicateBucketItem`, `SRPeerGetIDPSettings`, `SRPeerEdit`, `SRStateEdit`, and `SRPeerRemove`. Option parsers `getSRAddOptions`, `getSREditOptions`, and `getSRStatusOptions` translate query parameters into `madmin` option structures. `parseJSONBody` centralizes request-body reading, optional `madmin.DecryptData`, and JSON unmarshalling into site-replication request types.

The core dependency is `globalSiteReplicationSys`, which performs peer cluster mutations, applies replicated IAM/bucket metadata, calculates status, manages resync, exposes IDP settings, and handles network performance counters.

## Control Flow
Add/edit APIs validate admin permissions, decrypt client-supplied JSON with the authenticated secret key, parse `madmin.PeerSite` or `madmin.PeerInfo`, apply option flags, call `globalSiteReplicationSys.AddPeerClusters` or `EditPeerCluster`, and return JSON status. Peer join/edit/remove/state endpoints parse unencrypted internal peer JSON and delegate to `PeerJoinReq`, `PeerEditReq`, `InternalRemoveReq`, or `PeerStateEditReq`.

`SRPeerBucketOps` dispatches bucket operations based on route variable `operation`: make with versioning, configure replication, delete or force delete, and purge-deleted-bucket. It builds `MakeBucketOptions` from query parameters, including `createdAt`, lock, versioning, and force-create flags. `SRPeerReplicateIAMItem` dispatches `madmin.SRIAMItem` variants to peer handlers for policy, service account, policy mapping, STS credential, IAM user, and group changes. Policy bytes are parsed and empty policies are treated as nil/deletion semantics.

`SRPeerReplicateBucketItem` validates a bucket name and dispatches `madmin.SRBucketMeta` variants for bucket policy, quota, versioning, tags, object lock, SSE, lifecycle, or generic metadata update. Policy and quota payloads are parsed before peer handlers are called.

Status and metainfo APIs parse `madmin.SRStatusOptions`. `SiteReplicationStatus` defaults to buckets/users/policies/groups/ILM expiry rules when no option is specified for backward compatibility, then suppresses `ILMExpiryStats` unless at least one site has ILM expiry replication enabled. Resync op parses a peer site and dispatches start or cancel by route operation.

The dev-null and netperf endpoints are diagnostic paths. `SiteReplicationDevNull` streams request bytes into discard in 128 KiB chunks while updating `globalSiteNetPerfRX.RX`, and it treats early non-EOF errors as useful network instability logs. `SiteReplicationNetPerf` enforces a minimum duration and gob-encodes the result from `siteNetperf`.

## State And Persistence Behavior
Most handlers are stateful cluster operations. Peer add/edit/remove and state edit mutate the site-replication configuration and peer state. Peer IAM and bucket metadata endpoints apply replicated state from other clusters into local IAM stores and bucket metadata stores, using `UpdatedAt` timestamps carried in madmin replication payloads. Resync start/cancel updates resync state for a peer.

Request encryption is asymmetric by call type: client-initiated add/edit uses the caller's secret key, while many internal peer replication calls pass an empty encryption key to `parseJSONBody` and expect plain JSON over authenticated peer-admin channels. Bucket make/delete operations deliberately preserve metadata such as creation time and versioning/lock flags so peers can converge.

The diagnostic endpoints mutate only in-memory network performance counters and connection state, not persistent site-replication config.

## Dependencies And Integration Points
The file depends on `madmin-go/v3` site-replication request/response types, MinIO policy action constants, bucket metadata parsers, IAM policy parsers, mux route variables, humanize sizing constants, and internal discard helpers. It integrates with the IAM handlers in `admin-handlers-users.go` through site-replication hooks: those handlers emit `madmin.SRIAMItem` changes that this file's peer endpoint can apply on remote sites.

It also integrates with bucket lifecycle/metadata systems through replicated bucket metadata handlers and with network diagnostics through `globalSiteNetPerfRX` and `siteNetperf`.

## Risks And Test Signals
The main risks are authorization mistakes between external and internal endpoints, malformed or malicious replication payloads, and divergence caused by incorrectly parsed empty policy/quota payloads. `parseJSONBody` reads the whole body without an explicit size limit in this file, so callers rely on upstream admin limits and trusted peer channels. Peer endpoints that accept unencrypted payloads must remain protected by admin signature validation and site-replication operation policies.

Backward-compatibility behavior in `SiteReplicationStatus` is intentional: removing default status flags would change older clients. ILM-expiry stats suppression is another compatibility and response-size concern.

No direct tests for this file are included in the work item. Indirect signals should include site-replication integration tests for peer add/join/remove, IAM replication, bucket metadata replication, status filters, resync start/cancel, encrypted add/edit payloads, and netperf/dev-null behavior.
