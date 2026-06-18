# sources/object-store/minio/cmd/site-replication-utils.go

## Purpose
Manages site-replication resync status in memory and periodically persists it. It tracks resync state per peer deployment, per-bucket completion/failure, per-object progress, and admin-facing resync reports.

## Important APIs, Types, And Functions
`SiteResyncStatus` stores version, overall `ResyncStatusType`, peer deployment ID, per-bucket status map, total bucket count, and embedded `TargetReplicationResyncStatus`. `clone()` copies the bucket status map for safe readout. `siteResyncPrefix` defines the metadata storage prefix. `resyncState` maps a peer to a resync ID and last-save timestamp. `siteResyncMetrics` holds `resyncStatus` and `peerResyncMap` behind an RW mutex.

`newSiteResyncMetrics()` starts background `save()` and `init()` goroutines. `init()` retries `load()` with randomized sleeps until object layer/site-replication data is available. `load()` reads peer metadata via `loadSiteResyncMetadata()`. `report()` converts internal state to `madmin.SiteResyncMetrics`. `save()` periodically persists changed valid states via `saveSiteResyncMetadata()`. `updateState()`, `incBucket()`, `deleteBucket()`, `siteResyncStatus()`, `updateMetric()`, `status()`, and `siteStatus()` update and query resync progress.

## Control Flow
Initialization starts asynchronous load and save loops. Load waits for object-layer readiness and site-replication enablement, then imports peer resync metadata except for the local deployment. Save wakes on `siteResyncSaveInterval`, checks if site replication is enabled, finds statuses with valid states and newer `LastUpdate` than `LastSaved`, and saves them concurrently while holding the metrics lock. Runtime updates set state on resync start/end, update bucket statuses, delete removed buckets from active resyncs, aggregate object progress, and serve memory-first status queries with disk fallback.

## State And Persistence
State is both in-memory and persisted under the site-resync metadata path through `loadSiteResyncMetadata()` and `saveSiteResyncMetadata()`. In-memory maps are protected by `siteResyncMetrics` locks. Background goroutines run until the provided context is canceled. `LastSaved` prevents repeated saves of unchanged states.

## Dependencies And Integration Points
Depends on site-replication globals (`globalSiteReplicationSys`, `globalDeploymentID()`), object-layer access, metadata load/save helpers, `madmin-go` resync DTOs, `GlobalContext`, `UTCNow()`, resync option/status types, and target replication status types. It integrates with replication resync workflows, bucket deletion handling, admin status APIs, and metadata persistence.

## Risks And Edge Cases
Holding the metrics lock while launching and waiting for save goroutines serializes updates during persistence and can block hot paths if storage is slow. In `updateState()`, terminal state handling that misses an existing resync stores the zero value `st` and saves it, which deserves scrutiny because it may not persist the passed terminal status. `deleteBucket()` returns on the first missing/completed/failed status while iterating peers, so later peers may not be processed. The init retry loop sleeps without selecting on context during the sleep interval, delaying shutdown by up to roughly ten seconds.

## Test Signals
This hand-written file has no direct dedicated test in the listed sources. Generated codec tests cover `SiteResyncStatus` serialization only, not background load/save, status transitions, bucket deletion, or persistence error handling.
