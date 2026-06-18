# sources/object-store/minio/cmd/metacache.go

Purpose: This file defines the lifecycle state for a metacache listing and the core rules for keeping, refreshing, updating, and deleting cached listing data.

Important APIs and types: `scanStatus` has `scanStateNone`, `scanStateStarted`, `scanStateSuccess`, and `scanStateError`. `metacache` stores timestamps (`started`, `ended`, `lastHandout`, `lastUpdate`), bucket/root/filter/id, status, error text, recursive flag, file-not-found flag, and stream data version. Key methods are `finished`, `worthKeeping`, `keepAlive`, `update`, and `delete`; `baseDirFromPrefix` computes a listing base directory.

Control flow: `worthKeeping` removes stale running listings, old finished listings, and stale failed/none states. `keepAlive` periodically updates `lastHandout` through a local or remote peer while a request context is alive, and stops when the scan leaves `scanStateStarted`. `update` merges another metacache state into the current record, sets success/end timestamps, transitions away from started, marks clients missing after `metacacheMaxClientWait`, captures the first error, and preserves `fileNotFound`. `delete` validates bucket/id and asks the object layer to delete the `.metacache` prefix.

State and persistence behavior: The `metacache` struct is msgp-serializable and is the persisted/cache-manager record for listing state. The actual listing data is stored separately as metacache block objects. Deletion removes all cache data below the derived `.metacache` prefix through a `deleteAllStorager` object layer.

Dependencies and integration points: It interacts with peer REST `UpdateMetacacheListing`, `localMetacacheMgr`, global object-layer creation, `deleteAllStorager`, MinIO metadata bucket paths, and debug logging. It is constructed from `listPathOptions.newMetacache` and serialized by `metacache_gen.go`.

Risks: Lifecycle decisions are time-sensitive, so clock skew or slow clients can discard useful caches. `update` assigns `m.lastHandout = update.lastUpdate` when `update.lastHandout` is newer, which is subtle and should be reviewed before changing. `delete` depends on the global object layer being available and implementing `deleteAllStorager`.

Test signals: `metacache_test.go` checks `baseDirFromPrefix`, `finished`, and `worthKeeping` across successful, recursive, stale, errored, running, not-found, and week-old cases. Generated tests cover binary serialization.
