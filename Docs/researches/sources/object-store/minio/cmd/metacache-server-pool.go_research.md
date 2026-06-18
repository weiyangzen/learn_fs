# sources/object-store/minio/cmd/metacache-server-pool.go

## Purpose

`metacache-server-pool.go` implements erasure-server-pool listing over metacache. It handles old-cache cleanup, list argument normalization, cache lookup/resume/create decisions, multi-set listing fan-in, lifecycle/replication side effects, and async list saving.

## Important APIs, Control Flow, And State

`renameAllBucketMetacache` moves old per-bucket `.metacache` directories under `.minio.sys/tmp` for deletion. `(*erasureServerPools).listPath` validates list args, normalizes markers/prefixes/recursive flags/separators, parses cache markers, derives `BaseDir`, marks reserved/invalid buckets transient, and installs filters. If an ID exists and listing is not transient, it asks the hash-selected peer or local manager for the cache. Existing running/success caches are kept alive and resumed; missing/error caches clear the ID; peer failures fall back to transient listing.

When resuming with an ID, `listPath` either creates and saves a new cache via `listAndSave` or streams metadata parts from the recorded pool/set. On failure it truncates results, may asynchronously mark the remote cache as no longer used, and falls back to raw listing. Raw listing creates channels, runs `listMerged` in a goroutine, applies `gatherResults`, truncates to limit, and emits a new list ID when truncated and non-transient.

`listMerged` starts one `set.listPath` per erasure set, merges sorted streams with `mergeEntryChannels`, handles not-found/all-EOF cases, and returns significant errors. `triggerExpiryAndRepl` evaluates lifecycle expiration for latest and all versions and queues expiry and replication heal work. `listAndSave` chooses a pool/set with space, creates a `metaCacheRPC`, saves the full stream asynchronously while returning the first filtered page, and closes channels carefully when the caller returns.

State spans in-memory list options, peer metacache entries, saved metacache stream objects, and side-effect queues for expiry/replication.

## Risks And Test Signals

Risks include cancellation races among listing/saving/filter goroutines, fallback from cached to transient listing, stale or invalid pool/set markers, disk-full behavior, lifecycle deletes triggered by listing, and channel closure/backpressure. Direct tests are not in this subset; `metacache-entries_test.go` covers lower-level merge/filter/resolve pieces.
