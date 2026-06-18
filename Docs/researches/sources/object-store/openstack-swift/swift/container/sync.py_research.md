# sources/object-store/openstack-swift/swift/container/sync.py

## Purpose

`swift/container/sync.py` implements the container-sync daemon. It scans locally sync-enabled container DBs and mirrors object PUTs and DELETEs to a configured remote container. The daemon uses per-container sync points to divide work across local container replicas while still retrying older rows that may have been missed.

The file also contains a default internal-client configuration string used when `/etc/swift/internal-client.conf` is not present, so deployments can continue to run through upgrades.

## Important APIs, Types, and Functions

`ic_conf_body` is the fallback internal client pipeline. It includes catch_errors, proxy logging, cache, symlink, and proxy-server filters with account autocreation enabled.

`ContainerSync(Daemon)` initializes local device settings, scan interval and per-container time budget, sync realm validation, allowed hosts, optional HTTP proxies, a `ContainerSyncStore`, counters, the container ring, local bind identity, DB preallocation, connection timeout, and an `InternalClient`.

Core methods are `run_forever`, `run_once`, `report`, `container_report`, `container_sync`, `_update_sync_to_headers`, `_object_in_remote_container`, `container_sync_row`, and `select_http_proxy`.

`main()` is the daemon entry point.

## Control Flow

The scan starts from `ContainerSyncStore.synced_containers_generator()`, so only DBs with local sync symlinks are visited. For each path, `container_sync` opens a broker, removes stale sync-store entries when the DB is missing, checks that this node is one of the ring locations, skips object-versioning containers, extracts sync target/key and sync points, validates the sync target, and then runs two sync stages within `container_time`.

The first stage handles rows between `sync_point2` and `sync_point1`. These older rows are retried by all replicas to cover previous partial failures. Failed rows roll back the effective second sync point.

The second stage handles rows newer than `sync_point1`. Each row is assigned to one replica by hashing account/container/object and taking modulo replica count. `sync_point1` advances for every observed row so the next run can retry missed rows in the first stage.

`container_sync_row` decodes composite timestamps. Deleted rows send remote DELETEs using the tombstone data timestamp and accept remote `404`/`409`. Live rows HEAD the remote object and skip if it is already current; otherwise they fetch the newest local source object through the internal client, skip versioning symlinks, normalize headers, sign or key the remote PUT, stream the body, and update counters.

## State and Persistence Behavior

Persistent source state is in the container DB: `x_container_sync_point1`, `x_container_sync_point2`, sync metadata, and object rows. The daemon updates sync points throughout a run.

The sync-store symlink tree controls discovery but is maintained mainly by the container server and replicator. This daemon removes stale links when the linked DB is gone.

Remote object state is mutated by `delete_object` and `put_object`. Authentication state is per request and not persisted. Counters are in-memory and logged periodically.

## Dependencies and Integration Points

Important dependencies include `ContainerBroker`, `ContainerSyncStore`, `ContainerSyncRealms`, `validate_sync_to`, `Ring`, `is_local_device`, `InternalClient`, direct container-sync internal client helpers, versioned-write sysmeta constants, timestamp helpers, `decode_timestamps`, `hash_path`, `quote`, and `FileLikeIter`.

Integration points include container server metadata updates, container replicator sync-store refreshes, remote sync-capable clusters, and symlink middleware in the internal-client pipeline.

## Risks and Edge Cases

The two-sync-point algorithm is subtle. Advancing point1 too aggressively could skip rows; advancing point2 after failures could prevent retries. The current design retries older rows by all replicas while partitioning new rows by hash.

Stale sync-store symlinks are expected after races or crashes and are removed only for the specific missing-DB condition.

Local ordinal selection depends on ring device IP/port matching. Misconfiguration can cause no node or multiple nodes to sync rows.

Remote HEAD optimization depends on timestamp comparison. Timestamp bugs can skip necessary PUTs or generate redundant PUTs.

Object versioning is explicitly skipped, with a row-level symlink guard as a second protection.

For live rows, the source object GET can return an older timestamp than the row metadata; the code raises rather than pushing stale data.

## Test Signals

Useful tests should cover sync-store discovery and stale link removal, local ordinal selection, metadata skip/failure paths, two-stage sync-point advancement and rollback, hash partitioning, realm-auth and legacy headers, remote HEAD skip behavior, DELETE acceptable statuses and failures, PUT source GET and header normalization, versioning symlink skips, proxy selection, time-budget exits, and report counters.
