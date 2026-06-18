# sources/object-store/minio/cmd/site-replication.go

## Purpose

`site-replication.go` implements MinIO's cluster-level site replication coordinator. It links multiple MinIO deployments into one replication set, persists the membership and service-account state, fans out bucket and IAM mutations to peer sites, reports cross-site replication health, periodically heals divergent metadata, and controls site-wide resync operations. The file sits behind admin APIs and internal peer APIs; local S3/admin operations apply locally first, then hooks replicate the resulting metadata changes to peer clusters.

## Important APIs, types, and functions

- `SiteReplicationSys` is the central manager. It protects `enabled`, persisted `srState`, and the IAM metadata cache with locks.
- `srStateV1` / `srStateData` are the JSON persistence contract for `.minio.sys/config/site-replication/state.json`: local site name, peer map keyed by deployment ID, the site-replicator service account access key, and `UpdatedAt`.
- `SRError` wraps site replication failures with an `APIErrorCode`; helper constructors classify invalid requests, peer failures, backend issues, service-account failures, bucket/IAM metadata failures, and missing config.
- `AddPeerClusters`, `PeerJoinReq`, `RemovePeerCluster`, `InternalRemoveReq`, `EditPeerCluster`, `PeerEditReq`, and `PeerStateEditReq` implement membership lifecycle.
- `MakeBucketHook`, `DeleteBucketHook`, `IAMChangeHook`, and `BucketMetaHook` are local mutation hooks that propagate bucket, IAM, and metadata changes to peers.
- Peer handlers such as `PeerBucketMakeWithVersioningHandler`, `PeerBucketConfigureReplHandler`, `PeerIAMUserChangeHandler`, `PeerSvcAccChangeHandler`, `PeerPolicyMappingHandler`, and the bucket metadata handlers apply inbound replicated changes locally.
- `SiteReplicationStatus`, `siteReplicationStatus`, and `SiteReplicationMetaInfo` collect per-site metadata and compare buckets, policies, users, groups, ILM expiry rules, peer state, and metrics.
- The healing loop is rooted at `startHealRoutine`, which calls `healIAMSystem` and `healBuckets`; specific healers repair bucket existence, versioning, object lock, SSE, replication config, policies, tags, quotas, ILM expiry, users, groups, and policy mappings.
- `startResync`, `cancelResync`, `newSiteResyncStatus`, `loadSiteResyncMetadata`, and `saveSiteResyncMetadata` manage explicit site resync to a peer deployment.
- Helpers `getAdminClient`, `getS3Client`, `getPeerCreds`, `concDo`, `toErrorFromErrMap`, `getMissingSiteNames`, `mergeWithCurrentLCConfig`, and `siteReplicatorCred` support peer I/O, fan-out, status text, lifecycle merging, and cached secret-key lookup.

## Control flow

Initialization starts a leader-locked healing goroutine, then retries `loadFromDisk` until the persisted state is loaded or confirmed absent. Adding peers first probes each supplied endpoint via admin and S3 clients, validates unique deployment IDs, ensures the local deployment is present, requires existing sites to be included when extending an existing set, rejects conflicting bucket ownership, and checks that IDP settings match. It creates or reuses the `site-replicator-0` service account, sends `SRPeerJoin` to peers, persists the common peer map locally, caches the service account secret, and performs an initial bucket/IAM sync.

Replication hooks are invoked after local state has already changed. Bucket creation creates the bucket and versioning on every site, then configures remote targets and site-replication rules. Bucket deletion sends delete operations to peers. IAM and bucket metadata hooks call madmin peer APIs concurrently. `concDo` runs a local action for the current deployment and peer actions for every other deployment, builds an ordered error summary, and marks remote targets offline when network/host-down errors are detected.

Peer handlers are idempotent where possible. Bucket make tolerates already-existing buckets, forces versioning, optionally object lock, saves bucket metadata, and reloads metadata. IAM and bucket metadata handlers skip stale inbound updates by comparing the incoming `updatedAt` with local update timestamps. Policy, tagging, SSE, quota, and lifecycle handlers treat nil payloads as deletes where the API supports deletion. STS credentials are accepted only if the session token validates with the local token-signing key.

Status collection first gathers `madmin.SRInfo` from the local site and every peer. It builds cross-site union sets for buckets, users, groups, policies, policy mappings, and ILM expiry rules, then computes mismatch booleans and per-site totals. Public `SiteReplicationStatus` filters detailed maps so normal output emphasizes mismatches unless a specific entity type is requested. Meta collection can return only a requested entity and caches full IAM meta responses for one healing interval.

The heal routine runs every `siteHealTimeInterval` on the leader. It heals IAM before buckets, waits for low I/O between iterations, and logs slow refreshes. Healing is intentionally latest-wins: individual healers find the site with the most recent relevant timestamp, only act when the local site owns the latest value for IAM user/group/policy data, and push local latest metadata to peers. Bucket healing is special: only the local site that has the latest bucket create/delete timestamp coordinates make/delete/purge operations across sites.

Resync starts by validating that site replication is enabled, the peer exists, and the peer is not self. It creates a `SiteResyncStatus`, marks every bucket target for the peer with a reset ID and reset-before date, persists bucket target metadata, and starts the replication resyncer per bucket. Cancel clears matching reset IDs, updates bucket resync state, persists site metadata as canceled, and signals the resyncer.

## State and persistence behavior

Site membership persists as JSON under `getSRStateFilePath()` with an explicit format version. `saveToDisk` writes config, reloads site replication config across nodes through `globalNotificationSys`, then updates in-memory state. `removeFromDisk` deletes that config and clears the in-memory state. Because `saveToDisk` obtains the object layer dynamically, callers can fail with server-not-initialized if storage is not ready.

Bucket replication state is stored in bucket metadata: replication XML, target JSON, bucket policy JSON, tagging XML, versioning XML, object-lock XML, SSE XML, quota JSON, and lifecycle XML. Initial sync and healers update this metadata through `globalBucketMetadataSys` and `globalBucketTargetSys`, then rely on metadata reload/notification paths elsewhere in MinIO. Deleted bucket state uses `.minio.sys/buckets/.deleted/<bucket>` markers; `SRBucketDeleteOp` selects mark-delete, purge, or no-op behavior.

IAM state is stored in `globalIAMSys.store`, and replicated changes are applied through IAM system APIs. The site-replicator credential is both stored as a service account and cached in `globalSiteReplicatorCred`; `siteReplicatorCred.Get` lazily loads the secret key from the IAM store.

Resync state has two persistence layers: site-level msgp metadata under `siteResyncPrefix/<deployment-id>.meta` with a binary format/version header, and per-bucket replication target reset fields plus bucket resync status maintained by the replication pool. The code validates both file format and msgp version on load.

## Dependencies and integration points

This file is tightly integrated with MinIO globals: `globalIAMSys`, `globalBucketMetadataSys`, `globalBucketTargetSys`, `globalNotificationSys`, `globalReplicationPool`, `globalSiteResyncMetrics`, `globalLeaderLock`, `globalDeploymentID`, `globalRemoteTargetTransport`, `newObjectLayerFn`, DNS config, object-layer bucket APIs, and logger helpers. External APIs include `madmin-go/v3` for admin peer requests and DTOs, `minio-go/v7` for bucket listing during peer validation, MinIO internal lifecycle and replication packages for XML parsing/validation, LDAP helpers for DN validation, policy parsing/comparison, and `xsync` maps for IAM policy mapping loads.

Admin API integration is bidirectional: public admin calls invoke local `SiteReplicationSys` methods, and peer methods call madmin APIs such as `SRPeerJoin`, `SRPeerBucketOps`, `SRPeerReplicateIAMItem`, `SRPeerReplicateBucketMeta`, `SRPeerRemove`, `SRPeerEdit`, `SRStateEdit`, and `SRMetaInfo`. S3 replication integration occurs through generated bucket targets and replication rules with IDs prefixed `site-repl-<deployment-id>`.

## Risks and edge cases

- Add/join and edit/remove operations are multi-site and only partially transactional. Several paths return partial status after some peers were changed, and comments note manual cleanup may be needed after partial add failure.
- `AddPeerClusters` checks only some preconditions; a FIXME notes missing validation for global IAM policies and LDAP-created service accounts on peer clusters.
- Many healers choose the latest timestamp as authoritative. Clock skew or missing update timestamps can cause the wrong site to win.
- Several metadata healers ignore or log peer update failures and continue, so convergence may require repeated heal cycles.
- `concDo` requires callers to hold at least a read lock for stable `c.state`; misuse could race with state mutation.
- Status comparison helpers often skip parse failures and can under-report mismatches if malformed policy/lifecycle/replication data is ignored.
- The replication config status helper checks rule shape but does not deeply compare all destination semantics beyond rule count, prefix, and enabled features.
- `updateTargetEndpoints` ignores some per-bucket target list errors because healing should repair them later, which can leave edited endpoints partially applied until the heal loop succeeds.
- `mergeWithCurrentLCConfig` intentionally preserves transition actions while syncing expiry actions; this is subtle and can surprise callers expecting full lifecycle replication.
- Resync start can partially configure buckets; if every bucket fails it returns an error, otherwise failures are embedded in the operation status.

## Test signals

The paired test file in this subset only covers `getMissingSiteNames`, asserting that existing replicated sites missing from a new add request are reported by site name and that unrelated new deployments or no current sites do not produce names. There is no direct unit coverage here for add/join/remove transactions, replication hook fan-out, stale update handling, status mismatch computation, healing, lifecycle merge, or resync persistence. Most behavior likely depends on integration tests elsewhere because this file relies heavily on MinIO global systems and peer admin clients.
